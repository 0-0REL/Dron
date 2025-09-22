import cv2
from BlazeFaceDetection.blazeFaceDetector import blazeFaceDetector
#from ai_edge_litert.interpreter import Interpreter  # Solo LiteRT
from tflite_runtime.interpreter import Interpreter
import numpy as np
import time
import socket
import threading

class videoBroadcast():
	def __init__(self):
		# socket setting
		self.SOCKET_VIDEO_HOST = '0.0.0.0' 
		self.SOCKET_VIDEO_PORT = 5000
	def server(self):
		"""Socket para transmisión de video MJPEG"""
		global clients_connected, frame_with_overlay
		
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((self.SOCKET_VIDEO_HOST, self.SOCKET_VIDEO_PORT))
		server_socket.listen(5)
		print(f"Video socket connected to: {self.SOCKET_VIDEO_HOST}:{self.SOCKET_VIDEO_PORT}")
		
		while True:
			try:
				client_socket, addr = server_socket.accept()
				clients_connected = True
				print(f"Connection established from {addr}")
				
				# MJPEG stream Header
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

class FaceClassifier:
	def __init__(self, model:str = "BlazeFaceDetection/models/modelo.tflite"):
		# Initialize TFLite classifier model
		self.interpreter = Interpreter(model_path=model)
		self.interpreter.allocate_tensors()
		self.input_details = self.interpreter.get_input_details()
		self.output_details = self.interpreter.get_output_details()
		self.CARAS = {0: "Ignacio", 1: "Isis", 2: "Rodri", 3: "Rodrigo"}

	def predict(self,frame, startP, endP):
		for (start, end) in zip(startP, endP):
			x1, y1 = start
			x2, y2 = end
			roi = frame[y1:y2, x1:x2]
			if roi.size > 0:
				# Preprocess ROI for model
				model_input = cv2.resize(roi,(160,160))
				model_input = cv2.cvtColor(model_input, cv2.COLOR_BGR2RGB)
				model_input = model_input.astype(np.float32) / 255.0
				model_input = np.expand_dims(model_input, axis=0)
				# Run model inference
				self.interpreter.set_tensor(self.input_details[0]['index'], model_input)
				self.interpreter.invoke()
				output = self.interpreter.get_tensor(self.output_details[0]['index'])
				clase = np.argmax(output[0])
				prob = output[0][clase]
				# Show result
				if prob >= 0.70:
					nombre = self.CARAS[clase]
					color = (0, 255, 0)
				else:
					nombre = "?"
					color = (0, 0, 255)
				label = f"{nombre} ({prob:.2f})"
				cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

# Variables globales para comunicación
clients_connected = False
frame_with_overlay = None  # Variable global para el frame

if __name__ == "__main__":
	# Initialize webcam
	camera = cv2.VideoCapture(0)
	#cv2.namedWindow('Prueba', cv2.WINDOW_NORMAL)
	#cv2.resizeWindow('Prueba', 720, 480)  # Ancho, Alto

	# Initialize face detector and classifier
	faceDetector = blazeFaceDetector("back")# "front" or "back"
	classifier = FaceClassifier()
	okf = True

	# Initialize tracker
	ont = False
	tu = 0
	fps_interval = 1/25
	interval = 3 # 20 FPS
	first_run = True
	start_points = []
	#idframe = 0
	roi_x1 = 0
	roi_y1 = 0

	# Iniciar servidores en hilos separados
	threading.Thread(target=videoBroadcast().server, daemon=True).start()
	try:
		while camera.isOpened():
			ta = time.time()
			# Read frame from the webcam
			okf, frame = camera.read()
			frame = cv2.flip(frame, 1)
			roi_track = frame.copy()
			if len(start_points) > 0 and ont is False:
				x1, y1 = start_points[0]
				x2, y2 = end_points[0]
				bboxTck = (x1, y1, x2 - x1, y2 - y1)
				
				#tracker = cv2.TrackerKCF_create()
				tracker = cv2.legacy.TrackerMOSSE_create()
				tracker.init(frame, bboxTck)
				ont = True

			if ont:
				okt, bboxTck = tracker.update(frame)
				if okt:
					# Obtener coordenadas del tracker
					x1, y1, w, h = [int(v) for v in bboxTck]
					p1 = (x1, y1)
					p2 = (x1 + w, y1 + h)
					
					# 🔧 AGREGAR MARGEN al ROI (agrandar área)
					margin = 60  # Píxeles de margen alrededor del bbox
					height, width = frame.shape[:2]
					
					# Calcular nuevo ROI con margen (limitar a tamaño de imagen)
					roi_x1 = max(0, x1 - margin)
					roi_y1 = max(0, y1 - margin)
					roi_x2 = min(width, x1 + w + margin)
					roi_y2 = min(height, y1 + h + margin)
					
					# Extraer ROI agrandado
					roi_track = frame[roi_y1:roi_y2, roi_x1:roi_x2]
					cv2.rectangle(frame, p1, p2, (255, 0, 0), 2)
				else:
					ont = False
			if ta - tu >= interval or first_run:
				first_run = False
				# Detect faces
				detectionResults = faceDetector.detectFaces(roi_track)
				adjustedResults = []
				for (sx, sy, ex, ey) in detectionResults.boxes:
					# convertir normalizados → absolutos en el ROI
					sx = int(sx * roi_track.shape[1])
					ex = int(ex * roi_track.shape[1])
					sy = int(sy * roi_track.shape[0])
					ey = int(ey * roi_track.shape[0])

					# trasladar al frame global
					adjustedResults.append((
						sx + roi_x1, sy + roi_y1,
						ex + roi_x1, ey + roi_y1
					))
				# Draw detections
				img_plot, start_points, end_points = faceDetector.drawDetectionsMod(frame, adjustedResults)
				classifier.predict(frame, start_points, end_points)
				tu = ta
				if ont and len(start_points) > 0:
					del tracker
					ont = False
			
			# show frame
			#cv2.imshow("Prueba", frame)
			frame_with_overlay = frame.copy()
			#time.sleep(fps_interval)
			#idframe += 1
	except KeyboardInterrupt:
		print("Interrupted")
	#except Exception:
	#	print(":( Somthing went wrong", Exception)
	finally:
		camera.release()
		#cv2.destroyAllWindows()
