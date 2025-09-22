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
	# Initialize face detector
	modelType = "back"  # "front" or "back"
	faceDetector = blazeFaceDetector(modelType)
	# Initialize classifier
	classifier = FaceClassifier()
	okf = True
	#fps_interval = 1/25
	start_points = []
	idframe = 0
	try:
		while cv2.waitKey(1) != ord('q') and okf:
			# Read frame from the webcam
			okf, frame = camera.read()
			frame = cv2.flip(frame, 1)
			detectionResults = faceDetector.detectFaces(frame)
			img_plot, start_points, end_points = faceDetector.drawDetections(frame, detectionResults)
			classifier.predict(frame, start_points, end_points)
			# show frame
			cv2.imshow("Prueba", frame)
			#time.sleep(fps_interval)
			#idframe += 1
	except KeyboardInterrupt:
		print("Interrupted")
	#except Exception:
	#	print(":( Somthing went wrong", Exception)
	finally:
		camera.release()
		cv2.destroyAllWindows()