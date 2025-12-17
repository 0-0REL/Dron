import cv2
from BlazeFaceDetection.blazeFaceDetector import blazeFaceDetector
from ai_edge_litert.interpreter import Interpreter  # Solo LiteRT
import numpy as np
import time

class FaceClassifier:
	def __init__(self, model:str = "complementos/modelos/modelo_exportado/modelo.tflite"):
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

if __name__ == "__main__":
	# Initialize webcam
	#camera = cv2.VideoCapture("/home/rodrigo/Vídeos/Camera/prueba.webm")
	camera = cv2.VideoCapture(0)
	cv2.namedWindow('Prueba', cv2.WINDOW_NORMAL)
	cv2.resizeWindow('Prueba', 720, 480)  # Ancho, Alto
	cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
	cv2.resizeWindow("frame", 720,480)
	# Initialize face detector and classifier
	faceDetector = blazeFaceDetector("front")# "front" or "back"
	classifier = FaceClassifier()
	okf = True

	# Initialize tracker
	ont = False
	# Initialize variables
	tu = 0
	first_run = True
	start_points = []
	roi_x1 = 0
	roi_y1 = 0
	# debug
	fps_interval = 1/20
	interval = 1/10 # 2 Hz
	idframe = 0
	# variable test
	try:
		while cv2.waitKey(1) != ord('q') and camera.isOpened():
			ta = time.time()
			# Read frame from the webcam
			okf, frame = camera.read()
			frame = cv2.flip(frame, 1)
			roi_track = frame.copy()
			test = np.zeros_like(frame)
			if len(start_points) > 0 and ont is False:
				print(idframe, "arranca trakcer", start_points, end_points)
				x1, y1 = start_points[0]
				x2, y2 = end_points[0]

				margin = 50  # Píxeles de margen alrededor del bbox
				height, width = frame.shape[:2]
				# Calcular nuevo ROI con margen (limitar a tamaño de imagen)
				x1 = max(0, x1 - margin)
				y1 = max(0, y1 - margin)
				x2 = min(width, x2 + margin)
				y2 = min(height, y2 + margin)

				test[y1:y2, x1:x2] = frame[y1:y2, x1:x2]
				bboxTck = (x1, y1, x2 - x1, y2 - y1)
				
				x, y, w, h = bboxTck
				if w <= 0 or h <= 0 or x < 0 or y < 0 or (x + w) > width or (y + h) > height:
					pass
				else:
					tracker = cv2.TrackerKCF_create()
					tracker = cv2.legacy.TrackerMOSSE_create()
					print(idframe, "arranca trakcer", bboxTck)
					tracker.init(frame, bboxTck)
					ont = True

			if ont:
				okt, bboxTck = tracker.update(frame)
				if okt:
					print(idframe,"tracker activa")
					# Obtener coordenadas del tracker
					x1, y1, w, h = [int(v) for v in bboxTck]
					p1 = (x1, y1)
					p2 = (x1 + w, y1 + h)
					
					# Extraer ROI agrandado
					roi_x1, roi_y1 = p1
					roi_track = frame[p1[1]:p2[1], p1[0]:p2[0]]
					#print(idframe, roi_track)
					cv2.rectangle(frame, p1, p2, (255, 0, 0), 2)
				else:
					ont = False
					print(idframe, "lost")
			
			if ta - tu >= interval or first_run:
				first_run = False
				#if roi_track is None or roi_track.size == 0 or len(roi_track.shape) != 3:
				#	del tracker
				#	ont = False
				#	continue
				if roi_track is not None and roi_track.size > 0 and len(roi_track.shape) == 3:
					detectionResults = faceDetector.detectFaces(roi_track)
				else:
					del tracker
					ont = False
				
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

				img_plot, start_points, end_points = faceDetector.drawDetectionsMod(frame, adjustedResults)
				# Draw detections
				#img_plot, start_points, end_points = faceDetector.drawDetections(frame, detectionResults)
				classifier.predict(frame, start_points, end_points)
				tu = ta
				if ont and len(start_points) > 0:
					print(idframe, "reset tracker")
					del tracker
					ont = False
			
			# show frame
			cv2.imshow("Prueba", test)
			cv2.imshow("frame", frame)
			time.sleep(fps_interval)
			idframe += 1
	except KeyboardInterrupt:
		print("Interrupted")
	#except Exception:
	#	print(":( Somthing went wrong", Exception)
	finally:
		camera.release()
		cv2.destroyAllWindows()