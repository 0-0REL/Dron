import mediapipe as mp
import cv2
import time
import numpy as np
import os

START_TIME = time.time()
DETECTION_RESULT = None

cam = cv2.VideoCapture(0)

# Directorio para guardar rostros
output_dir = "tensor/dataset/rodri"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

frame_count = 1
last_face = None  # Para guardar el último rostro detectado

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
    while True:
        ok, frm = cam.read()
        if not ok:
            print('Error')
            break
            
        frm_rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frm_rgb)
        
        frame_timestamp_ms = int((time.time() - START_TIME) * 1000)
        # un ejemplo de mediapipe usa como time stamp -> time.time_ns() // 1_000_000
        detector.detect_async(mp_image, frame_timestamp_ms)
        
        if DETECTION_RESULT:
            frm, st, ed = visualize(frm, DETECTION_RESULT)
            face = frm[st[1]:ed[1], st[0]:ed[0]]
            if face.size > 0:  # Verificar que el recorte no esté vacío
                #face_resized = cv2.resize(face, (250, 250))
                last_face = face  # Guarda el último rostro detectado


        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC para salir
            break
        elif key == ord('s'):
            if last_face is not None:
                filename = f"{output_dir}/rostro_{frame_count}.jpg"
                cv2.imwrite(filename, last_face)
                print(f"Rostro guardado: {filename}")
                frame_count += 1

        cv2.rectangle(frm, st, ed, (0, 165, 255), 3)
        cv2.imshow('face_detection', cv2.flip(frm,1))

cam.release()
cv2.destroyAllWindows()