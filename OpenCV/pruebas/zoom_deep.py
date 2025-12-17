# Programa en media pipe que funciona segun como muestra la documentacion que de debe configurar
# y usar
import mediapipe as mp
import cv2
import time
import numpy as np

START_TIME = time.time()
DETECTION_RESULT = None

# Nuevas constantes para el zoom
ZOOM_THRESHOLD = 9000  # Ajustar según necesidad (área mínima para activar zoom)
ZOOM_FACTOR = 2         # Factor de ampliación
ZOOM_MARGIN = 30        # Margen alrededor del rostro

cam = cv2.VideoCapture(0)

BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
FaceDetectorResult = mp.tasks.vision.FaceDetectorResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a face detector instance with the live stream mode:
def print_result(result: FaceDetectorResult, output_image: mp.Image, timestamp_ms: int):
    global DETECTION_RESULT
    DETECTION_RESULT = result

def visualize(image, detection_result) -> np.ndarray:
    if detection_result is None:
        return image
        
    for detection in detection_result.detections:
        bbox = detection.bounding_box
        start_point = bbox.origin_x, bbox.origin_y
        end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        cv2.rectangle(image, start_point, end_point, (0, 165, 255), 3)
    
    return image

def apply_zoom(frame, detection):
    h, w = frame.shape[:2]
    bbox = detection.bounding_box
    
    # Calcula el centro del rostro
    center_x = bbox.origin_x + bbox.width // 2
    center_y = bbox.origin_y + bbox.height // 2
    
    # Calcula la región de zoom
    new_width = int(w / ZOOM_FACTOR)
    new_height = int(h / ZOOM_FACTOR)
    
    # Aplica márgenes
    new_width = min(new_width + ZOOM_MARGIN, w)
    new_height = min(new_height + ZOOM_MARGIN, h)
    
    # Calcula coordenadas del área a recortar
    x1 = max(0, center_x - new_width // 2)
    y1 = max(0, center_y - new_height // 2)
    x2 = min(w, x1 + new_width)
    y2 = min(h, y1 + new_height)
    
    # Ajusta coordenadas si se excede el tamaño
    if x2 - x1 < new_width:
        x1 = max(0, x2 - new_width)
    if y2 - y1 < new_height:
        y1 = max(0, y2 - new_height)
    
    # Recorta y redimensiona
    cropped = frame[y1:y2, x1:x2]
    if cropped.size == 0:
        return frame
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

options = FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path='src/blaze_face_short_range.tflite'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

with FaceDetector.create_from_options(options) as detector:
    while True:
        ok, frm = cam.read()
        if not ok:
            print('Error')
            break
            
        frm_rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frm_rgb)
        
        frame_timestamp_ms = int((time.time() - START_TIME) * 1000)
        detector.detect_async(mp_image, frame_timestamp_ms)
        
        if DETECTION_RESULT:
            frm = visualize(frm, DETECTION_RESULT)
            
            # Aplica zoom si se detecta área pequeña
            for detection in DETECTION_RESULT.detections:
                bbox = detection.bounding_box
                area = bbox.width * bbox.height
                
                if area < ZOOM_THRESHOLD:
                    frm = apply_zoom(frm, detection)
                    break  # Solo aplica a la primera detección

        cv2.imshow('face_detection', cv2.flip(frm, 1))

        if cv2.waitKey(1) == 27:
            break

cam.release()
cv2.destroyAllWindows()