# Programa en media pipe que funciona segun como muestra la documentacion que de debe configurar
# y usar
import mediapipe as mp
import cv2
import time
import numpy as np

START_TIME = time.time()
DETECTION_RESULT = None

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
    #print('face detector result: {}'.format(result))

def visualize(image, detection_result) -> np.ndarray:
    """Draws bounding boxes on the input image and return it.
    Args:
        image: The input RGB image.
        detection_result: The list of all "Detection" entities to be visualized.
    Returns:
        Image with bounding boxes.
    """
    if detection_result is None:
        return image
        
    for detection in detection_result.detections:
        # Draw bounding_box
        bbox = detection.bounding_box
        start_point = bbox.origin_x, bbox.origin_y
        end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        # Use the orange color for high visibility.
        cv2.rectangle(image, start_point, end_point, (0, 165, 255), 3)
    
    return image

options = FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path='blaze_face_short_range.tflite'),
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
        # un ejemplo de mediapipe usa como time stamp -> time.time_ns() // 1_000_000
        detector.detect_async(mp_image, frame_timestamp_ms)
        
        if DETECTION_RESULT:
            frm = visualize(frm, DETECTION_RESULT)

        cv2.imshow('face_detection', cv2.flip(frm,1))

        # Stop the program if the ESC key is pressed.
        if cv2.waitKey(1) == 27:
            break

cam.release()
cv2.destroyAllWindows()