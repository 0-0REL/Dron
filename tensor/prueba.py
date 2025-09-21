import cv2
import mediapipe as mp
import time
import numpy as np
from ai_edge_litert.interpreter import Interpreter

interpreter = Interpreter(model_path="tensor/modelo_exportado/modelo.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

START_TIME = time.time()
DETECTION_RESULT = None

cam = cv2.VideoCapture(0)
BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
FaceDetectorResult = mp.tasks.vision.FaceDetectorResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a face detector instance with the live stream mode:
def print_result(result, output_image: mp.Image, timestamp_ms: int):
    global DETECTION_RESULT
    DETECTION_RESULT = result
    #print('face detector result: {}'.format(result))

def visualize(image, detection_result) -> np.ndarray:
    """Draws bounding boxes on the input image and return it.
    Args:
        image: The input RGB image.
        detection_result: The list of all "Detection" entities to be visualized.
    Returns:
        Image with bounding boxes.
    """
    start_point = (0, 0)
    end_point = (0, 0)
    if detection_result is None:
        return image, (0,0), (0,0)
        
    for detection in detection_result.detections:
        # Draw bounding_box
        bbox = detection.bounding_box
        start_point = bbox.origin_x, bbox.origin_y
        end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        # Use the orange color for high visibility.
        #print('Area: ', bbox.width * bbox.height)
    
    return image, start_point, end_point

options = FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path='complementos/modelos/blaze_face_short_range.tflite'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

st = (0,0)
ed = (0,0)

with FaceDetector.create_from_options(options) as detector:
    while cv2.waitKey(1) != 27:
        ok, frm = cam.read()
        if not ok:
            print('Error')
            break
        frm = cv2.flip(frm, 1)
            
        frm_rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frm_rgb)
        
        frame_timestamp_ms = int((time.time() - START_TIME) * 1000)
        # un ejemplo de mediapipe usa como time stamp -> time.time_ns() // 1_000_000
        detector.detect_async(mp_image, frame_timestamp_ms)
        
        if DETECTION_RESULT:
            frm, st, ed = visualize(frm, DETECTION_RESULT)
            face = frm[st[1]:ed[1], st[0]:ed[0]]
            if face.size > 0:  # Verificar que el recorte no esté vacío
                face_resized = cv2.resize(face, (160, 160))
                face_resized = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
                face_array = face_resized.astype(np.float32) / 255.0
                face_array = np.expand_dims(face_array, axis=0)

                interpreter.set_tensor(input_details[0]['index'], face_array)
                interpreter.invoke()
                output = interpreter.get_tensor(output_details[0]['index'])
                clase = np.argmax(output[0])
                prob = output[0][clase]

                caras = {0: "ignacio", 1: "Isis", 2: "Rodri", 3: "Rodrigo"}

                if prob >= 0.70:
                    nombre = caras[clase]
                    color = (0, 255, 0)
                else:
                    nombre = "Desconocido"
                    color = (0, 0, 255)
                label = f"{nombre} ({prob:.2f})"
                cv2.putText(frm, label, (st[0], st[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.rectangle(frm, st, ed, (0, 165, 255), 3)
        cv2.imshow('face_detection', frm)

cam.release()
cv2.destroyAllWindows()