#!/usr/bin/env python3
#ROS
import rospy
from geometry_msgs.msg import Vector3
#
import cv2
from BlazeFaceDetection.blazeFaceDetector import blazeFaceDetector
import numpy as np
import socket
import threading
import json
import time
import os
import math
# tflite_runtime (RPI) | ai_edge_litert (PC)
from tflite_runtime.interpreter import Interpreter

# Configuración de sockets
SOCKET_VIDEO_HOST = '0.0.0.0' 
SOCKET_VIDEO_PORT = 5000

# Variables globales para comunicación
clients_connected = False
frame_with_overlay = None  # Variable global para el frame
ahrs_cam = Vector3()
ahrs_cam.x = 0.0
ahrs_cam.y = 0.0
ahrs_cam.z = 0.0

def video_socket_server():
    """Socket para transmisión de video MJPEG"""
    global clients_connected, frame_with_overlay
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SOCKET_VIDEO_HOST, SOCKET_VIDEO_PORT))
    server_socket.listen(5)
    print(f"Socket de video escuchando en {SOCKET_VIDEO_HOST}:{SOCKET_VIDEO_PORT}")
    
    while True:
        try:
            client_socket, addr = server_socket.accept()
            clients_connected = True
            print(f"Conexión de video desde {addr}")
            
            # Encabezado MJPEG stream
            client_socket.sendall(
                b'HTTP/1.1 200 OK\r\n'
                b'Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n'
            )
            
            while True:
                if frame_with_overlay is not None:
                    try:
                        # Codificar frame como JPEG
                        _, jpeg_frame = cv2.imencode('.jpg', frame_with_overlay, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        
                        # Enviar frame
                        client_socket.sendall(
                            b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' +
                            jpeg_frame.tobytes() +
                            b'\r\n'
                        )
                    except Exception as e:
                        print(f"Error enviando video: {e}")
                        break
                time.sleep(0.033)  # ~30 FPS
                
        except Exception as e:
            print(f"Error en socket de video: {e}")
            clients_connected = False
            time.sleep(1)

def callbackAhrs(datoAhrs):
    global ahrs_cam
    ahrs_cam = datoAhrs

def angOff(frm, escala=1):
        global ahrs_cam
        frm = cv2.resize(frm, dsize=None, fx=escala, fy=escala)
        (h, w) = frm.shape[:2]
        centro = (w//2, h//2)
        Mrot = cv2.getRotationMatrix2D(centro, -ahrs_cam.y, 1.0)
        rot_img = cv2.warpAffine(frm, Mrot, (w, h))
        altCent = int(centro[1] * (1 + math.tan(math.radians(-ahrs_cam.x))))
        if altCent > h:
            altCent = h
        elif altCent < 0:
            altCent = 0
        #cv2.circle(rot_img, (centro[0], altCent), 5, (0,0,255), -1)
        return rot_img

# Iniciar servidores en hilos separados
threading.Thread(target=video_socket_server, daemon=True).start()

# Tu código original de procesamiento de video
def faceReco():
    # Inicia ROS
    rospy.init_node('faceReco', anonymous=False)
    pub = rospy.Publisher('/faceCoord', Vector3, queue_size=5)
    rospy.Subscriber("ahrs_mpu", Vector3, callbackAhrs)
    rate = rospy.Rate(20) # 20hz
    vecDetc = Vector3()
    # Incia camara de detector
    source = cv2.VideoCapture(0)
    scoreThreshold = 0.7
    iouThreshold = 0.3
    modelType = "front"
    global frame_with_overlay
    # Inicializar modelo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_path = os.path.join(script_dir, "BlazeFaceDetection", "models", "modelo.tflite")
    interpreter = Interpreter(model_path=models_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    # Initialize face detector
    faceDetector = blazeFaceDetector(modelType, scoreThreshold, iouThreshold)

    # Variables para cálculo de FPS
    prev_time = time.time()
    fps = 0
    while not rospy.is_shutdown():
        current_time = time.time()
        has_frame, frame = source.read()
        if not has_frame:
            break
        #frame = cv2.flip(frame, 1)
        frame = angOff(frame)
        # Detect faces
        detectionResults = faceDetector.detectFaces(frame)
        # Draw detections
        img_plot, top, bottom = faceDetector.drawDetections(frame, detectionResults)
        # Recorta y prepara el rostro para el modelo TFLite
        face = frame[top[1]:bottom[1], top[0]:bottom[0]]
        if face.size > 0:
            vecDetc.x = (top[0] + bottom[0]) // 2
            vecDetc.y = (top[1] + bottom[1]) // 2
            vecDetc.z = face.shape[1] * face.shape[0]
            pub.publish(vecDetc)
            
            face_resized = cv2.resize(face, (160, 160))
            face_resized = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
            face_array = face_resized.astype(np.float32) / 255.0
            face_array = np.expand_dims(face_array, axis=0)

            interpreter.set_tensor(input_details[0]['index'], face_array)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details[0]['index'])
            clase = np.argmax(output[0])
            prob = output[0][clase]

            # Predecir rostro
            if clase == 1 and prob >= 0.7:
                nombre = "Ignacio"
                color = (255, 255, 0)
            elif clase == 2 and prob >= 0.7:
                nombre = "Rodrigo"
                color = (0, 255, 0)
            else:
                nombre = "Desconocido"
                color = (0, 0, 255)
                clase = 0

            label = f"{nombre} ({prob:.2f})"
            cv2.putText(frame, label, (top[0], top[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # Guardar frame para el stream de video
        elapsed_time = current_time - prev_time
        if elapsed_time > 0:
            fps = 1.0 / elapsed_time
        prev_time = current_time

        # --- Mostrar FPS en la esquina superior derecha ---
        (h, w) = frame.shape[:2]
        fps_text = f"FPS: {fps:.2f}"
        cv2.putText(frame, fps_text, (w - 150, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 255), 2)
        frame_with_overlay = frame.copy()
        rate.sleep()

if __name__ == '__main__':
    try:
        faceReco()
    except rospy.ROSInterruptException:
        print("Programa terminado por el usuario")
