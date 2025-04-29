# Programa que para detectar y coordinar dron mediante el rostro detectado
import mediapipe as mp
import cv2
import time
import numpy as np
from simple_pid import PID

START_TIME = time.time()
DETECTION_RESULT = None

# Configuraciones
cam = cv2.VideoCapture(0)
#cam = cv2.VideoCapture("complementos/video.avi")

pid_thr = PID(1, 0, 0, 0, output_limits=(1e3,2e3)) # Set 0 distancia en x
pid_yaw = PID(1, 0, 0, 0, output_limits=(-500,500)) # set 0 distancia en y
pid_pitch = PID(0.5, 0, 0, 13e3, output_limits=(-500,500)) # set area a distancia permitida

BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
FaceDetectorResult = mp.tasks.vision.FaceDetectorResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a face detector instance with the live stream mode:
def resultado(result: FaceDetectorResult, output_image: mp.Image, timestamp_ms: int):
    global DETECTION_RESULT
    DETECTION_RESULT = result
    #print('face detector result: {}'.format(result))

def mostrar(imagen, detection_result) -> np.ndarray:
    """Draws bounding boxes on the input image and return it.
    Args:
        image: The input RGB image.
        detection_result: The list of all "Detection" entities to be visualized.
    Returns:
        Image with bounding boxes.
    """
    if detection_result is None:
        return imagen
        
    for deteccion in detection_result.detections:
        # Dibuja un punto al centro de la cara
        bbox = deteccion.bounding_box
        punto = bbox.origin_x + bbox.width//2, bbox.origin_y + bbox.height//2
        cv2.circle(imagen, punto, 5, (0, 0, 255), -1)
        Area = bbox.width*bbox.height
        #print('Area:', Area)
        #print('adelante:', pid_pitch(Area))
    
    return imagen

options = FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path='src/blaze_face_short_range.tflite', delegate=mp.tasks.BaseOptions.Delegate.GPU),
    running_mode=VisionRunningMode.LIVE_STREAM, result_callback=resultado)

with FaceDetector.create_from_options(options) as detector:
    while True:
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
            frm = mostrar(frm, DETECTION_RESULT)

        cv2.imshow('Rostro',frm)

        # Stop the program if the ESC key is pressed.
        if cv2.waitKey(1) == 27:
            break

cam.release()
cv2.destroyAllWindows()