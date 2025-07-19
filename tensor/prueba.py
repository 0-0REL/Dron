import cv2
import numpy as np
from ai_edge_litert.interpreter import Interpreter

interpreter = Interpreter(model_path="tensor/modelo_exportado/modelo.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

source = cv2.VideoCapture(0)
win_name = "Camera Preview"
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)

net = cv2.dnn.readNetFromCaffe(
    "complementos/modelos/deploy.prototxt",
    "complementos/modelos/res10_300x300_ssd_iter_140000_fp16.caffemodel"
)
in_width = 300
in_height = 300
mean = [104, 117, 123]
conf_threshold = 0.7

while cv2.waitKey(1) != 27:
    has_frame, frame = source.read()
    if not has_frame:
        break
    frame = cv2.flip(frame, 1)
    frame_height = frame.shape[0]
    frame_width = frame.shape[1]

    blob = cv2.dnn.blobFromImage(frame, 1.0, (in_width, in_height), mean, swapRB=False, crop=False)
    net.setInput(blob)
    detections = net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x_top_left = int(detections[0, 0, i, 3] * frame_width)
            y_top_left = int(detections[0, 0, i, 4] * frame_height)
            x_bottom_right = int(detections[0, 0, i, 5] * frame_width)
            y_bottom_right = int(detections[0, 0, i, 6] * frame_height)

            # Recorta y prepara el rostro para el modelo TFLite
            face = frame[y_top_left:y_bottom_right, x_top_left:x_bottom_right]
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
                elif clase == 2 and prob >= 0.7:
                    nombre = "Rodrigo"
                    color = (0, 255, 0)
                else:
                    nombre = "Desconocido"
                    color = (0, 0, 255)
                    clase = 0  # fuerza clase 0 si no supera el umbral

                label = f"{nombre} ({prob:.2f})"
                cv2.rectangle(frame, (x_top_left, y_top_left), (x_bottom_right, y_bottom_right), color, 2)
                cv2.putText(frame, label, (x_top_left, y_top_left - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            else:
                cv2.rectangle(frame, (x_top_left, y_top_left), (x_bottom_right, y_bottom_right), (0, 255, 0), 2)

    t, _ = net.getPerfProfile()
    label = "Inference time: %.2f ms" % (t * 1000.0 / cv2.getTickFrequency())
    cv2.putText(frame, label, (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
    cv2.imshow(win_name, frame)

source.release()
cv2.destroyWindow(win_name)