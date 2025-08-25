#ROS
import rospy
#
import cv2
from BlazeFaceDetection.blazeFaceDetector import blazeFaceDetector
import numpy as np
import socket
import threading
import json
import time
# CAMBIO IMPORTANTE: Usar tflite_runtime en lugar de ai_edge_litert
from tflite_runtime.interpreter import Interpreter

# Configuración de sockets
SOCKET_DATA_HOST = '0.0.0.0'
SOCKET_DATA_PORT = 5000
SOCKET_VIDEO_HOST = '0.0.0.0' 
SOCKET_VIDEO_PORT = 5001

# Inicializar modelo (MODIFICADO para tflite_runtime)
interpreter = Interpreter(model_path="models/modelo.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Variables globales para comunicación
dato = [1, 2, 3]
clients_connected = False
frame_with_overlay = None  # Variable global para el frame

def data_socket_server():
    """Socket para enviar datos JSON"""
    global dato, clients_connected
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SOCKET_DATA_HOST, SOCKET_DATA_PORT))
    server_socket.listen(5)
    print(f"Socket de datos escuchando en {SOCKET_DATA_HOST}:{SOCKET_DATA_PORT}")
    
    while True:
        try:
            client_socket, addr = server_socket.accept()
            clients_connected = True
            print(f"Conexión de datos desde {addr}")
            
            while True:
                # Enviar datos como JSON
                data_json = json.dumps({
                    "dato": dato,
                    "timestamp": time.time()
                })
                client_socket.sendall((data_json + '\n').encode())
                time.sleep(0.1)  # 10 FPS para datos
                
        except Exception as e:
            print(f"Error en socket de datos: {e}")
            clients_connected = False
            time.sleep(1)

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
                        _, jpeg_frame = cv2.imencode('.jpg', frame_with_overlay, 
                                                   [cv2.IMWRITE_JPEG_QUALITY, 80])
                        
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

# Iniciar servidores en hilos separados
threading.Thread(target=data_socket_server, daemon=True).start()
threading.Thread(target=video_socket_server, daemon=True).start()

# Tu código original de procesamiento de video
def faceReco():
source = cv2.VideoCapture(0)
scoreThreshold = 0.7
iouThreshold = 0.3
modelType = "front"
# Initialize face detector
faceDetector = blazeFaceDetector(modelType, scoreThreshold, iouThreshold)

try:
    while True:
        has_frame, frame = source.read()
        if not has_frame:
            break
        frame = cv2.flip(frame, 1)

        # Detect faces
        detectionResults = faceDetector.detectFaces(frame)

        # Draw detections
        img_plot, top, bottom = faceDetector.drawDetections(frame, detectionResults)
        # Recorta y prepara el rostro para el modelo TFLite
        face = frame[top[1]:bottom[1], top[0]:bottom[0]]
        if face.size > 0:
            face_resized = cv2.resize(face, (160, 160))
            face_resized = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
            face_array = face_resized.astype(np.float32) / 255.0
            face_array = np.expand_dims(face_array, axis=0)

            interpreter.set_tensor(input_details[0]['index'], face_array)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details[0]['index'])
            clase = np.argmax(output[0])
            prob = output[0][clase]

            # Nueva lógica de umbral
            if clase == 1 and prob >= 0.7:
                nombre = "Ignacio"
                color = (255, 255, 0)
                dato = [1, 0, 0]  # Ejemplo: dato para Ignacio
            elif clase == 2 and prob >= 0.7:
                nombre = "Rodrigo"
                color = (0, 255, 0)
                dato = [0, 1, 0]  # Ejemplo: dato para Rodrigo
            else:
                nombre = "Desconocido"
                color = (0, 0, 255)
                clase = 0
                dato = [0, 0, 1]  # Ejemplo: dato para Desconocido

            label = f"{nombre} ({prob:.2f})"
            #cv2.rectangle(frame, (x_top_left, y_top_left), (x_bottom_right, y_bottom_right), color, 2)
            cv2.putText(frame, label, (top[0], top[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        #else:
        #    cv2.rectangle(frame, (x_top_left, y_top_left), (x_bottom_right, y_bottom_right), (0, 255, 0), 2)


        # Guardar frame para el stream de video
        frame_with_overlay = frame.copy()
        
except KeyboardInterrupt:
    print("Programa terminado por el usuario")
finally:
    source.release()
