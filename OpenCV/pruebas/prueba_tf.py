import cv2
import numpy as np
from ai_edge_litert.interpreter import Interpreter

# Cargar modelo
interpreter = Interpreter(model_path="complementos/modelos/blaze_face_short_range.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_height = input_details[0]['shape'][1]
input_width = input_details[0]['shape'][2]

# Preprocesamiento de imagen
def preprocess(frame):
    img = cv2.resize(frame, (input_width, input_height))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32)
    img = np.expand_dims(img, axis=0)  # Añadir batch dimension
    return img

# Postprocesamiento (simplificado, solo bounding boxes)
def postprocess(outputs, frame_shape):
    boxes = outputs[0][0]   # bounding boxes normalizados
    scores = outputs[1][0]  # probabilidades

    h, w, _ = frame_shape
    results = []
    for i in range(len(scores)):
        if scores[i] > 0.5:  # umbral de confianza
            ymin, xmin, ymax, xmax = boxes[i]
            # Escalar a pixeles
            x1, y1 = int(xmin * w), int(ymin * h)
            x2, y2 = int(xmax * w), int(ymax * h)
            results.append(((x1, y1, x2, y2), scores[i]))
    return results

# Cámara
cam = cv2.VideoCapture(0)

while True:
    ok, frame = cam.read()
    if not ok:
        break

    img = preprocess(frame)

    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()

    # BlazeFace normalmente tiene 2 salidas: boxes y scores
    boxes = interpreter.get_tensor(output_details[0]['index'])
    scores = interpreter.get_tensor(output_details[1]['index'])

    detections = postprocess([boxes, scores], frame.shape)

    for (x1, y1, x2, y2), score in detections:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 2)
        cv2.putText(frame, f"{score:.2f}", (x1, y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,165,255), 1)

    cv2.imshow("face_detection_ai_edge", frame)

    if cv2.waitKey(1) == 27:
        break

cam.release()
cv2.destroyAllWindows()
