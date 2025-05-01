import mediapipe as mp
import cv2
import time
import numpy as np

# Configuración inicial
START_TIME = time.time()
DETECTION_RESULT = None
cam = cv2.VideoCapture(0)
tracker = cv2.legacy.TrackerMOSSE.create()

# Configuración de MediaPipe
BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
FaceDetectorResult = mp.tasks.vision.FaceDetectorResult
VisionRunningMode = mp.tasks.vision.RunningMode

def print_result(result: FaceDetectorResult, output_image: mp.Image, timestamp_ms: int):
    global DETECTION_RESULT
    DETECTION_RESULT = result

def visualize(image, detection_result):
    if detection_result is None:
        return image, None
        
    for detection in detection_result.detections:
        bbox = detection.bounding_box
        start_point = bbox.origin_x, bbox.origin_y
        end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        cv2.rectangle(image, start_point, end_point, (0, 165, 255), 3)
        return image, (int(bbox.origin_x), int(bbox.origin_y), 
                      int(bbox.width), int(bbox.height))
    return image, None

# Configuración del detector de rostros
options = FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path='src/blaze_face_short_range.tflite'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

tracking_active = False

with FaceDetector.create_from_options(options) as detector:
    while True:
        ok, frame = cam.read()
        if not ok:
            print("Error de captura")
            break

        # Procesamiento de imagen
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        frame_timestamp_ms = int((time.time() - START_TIME) * 1000)
        detector.detect_async(mp_image, frame_timestamp_ms)

        if tracking_active:
            # Seguimiento del objeto
            success, bbox = tracker.update(frame)
            if success:
                x, y, w, h = [int(v) for v in bbox]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            else:
                tracking_active = False
                cv2.putText(frame, "Fallo en seguimiento", (80, 140), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255), 2)
        else:
            # Detección inicial
            if DETECTION_RESULT:
                frame, bbox = visualize(frame, DETECTION_RESULT)
                if bbox:
                    tracker.init(frame, bbox)
                    tracking_active = True

        # Mostrar resultado
        flipped_frame = cv2.flip(frame, 1)
        cv2.imshow('Face Detection & Tracking', flipped_frame)

        # Salir con ESC
        if cv2.waitKey(1) == 27:
            break

cam.release()
cv2.destroyAllWindows()