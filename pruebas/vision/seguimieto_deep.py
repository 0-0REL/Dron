import mediapipe as mp
import cv2
import time
import numpy as np

DETECTION_RESULT = None
cam = cv2.VideoCapture(0)

# Configuración Kalman Filter para área
class AreaKalmanFilter:
    def __init__(self):
        self.kf = cv2.KalmanFilter(3, 1)
        self.kf.transitionMatrix = np.array([[1,1,0], 
                                           [0,1,1], 
                                           [0,0,1]], np.float32)
        self.kf.measurementMatrix = np.array([[1,0,0]], np.float32)
        self.kf.processNoiseCov = 1e-5 * np.eye(3, dtype=np.float32)
        self.kf.measurementNoiseCov = 1e-2 * np.eye(1, dtype=np.float32)
        self.kf.errorCovPost = np.eye(3, dtype=np.float32)
        self.last_area = 0
        
    def update(self, measurement):
        self.kf.predict()
        mp = np.array([[measurement]], np.float32)
        self.kf.correct(mp)
        state = self.kf.statePost
        self.last_area = state[0][0]
        return self.last_area

# Configuración MediaPipe
BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

def print_result(result, output_image: mp.Image, timestamp_ms: int):
    global DETECTION_RESULT
    DETECTION_RESULT = result

def bbox_mp(detecciones):
    if not detecciones.detections:
        return None
    bbox = detecciones.detections[0].bounding_box     
    return (int(bbox.origin_x), int(bbox.origin_y), 
            int(bbox.width), int(bbox.height))

# Configuración detector y tracker CSRT
options = FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path='src/blaze_face_short_range.tflite'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

tracker = cv2.TrackerCSRT_create()
area_kf = AreaKalmanFilter()
AREA_THRESHOLD = 10000
HYSTERESIS = 1500  # Margen para evitar oscilaciones

okt = False
with FaceDetector.create_from_options(options) as detector:
    while True:
        ok, frm = cam.read()
        if not ok:
            print('Error')
            break
            
        frm = cv2.flip(frm, 1)
        
        if not okt:
            # Modo detección MediaPipe
            frm_rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frm_rgb)
            detector.detect_async(mp_image, time.time_ns() // 1_000_000)
            
            if DETECTION_RESULT:
                bbox = bbox_mp(DETECTION_RESULT)
                if bbox:
                    cv2.circle(frm, (bbox[0]+bbox[2]//2, bbox[1]+bbox[3]//2), 5, (0,0,255),-1)
                    area = bbox[2] * bbox[3]
                    if area < (AREA_THRESHOLD - HYSTERESIS):
                        tracker.init(frm, bbox)
                        area_kf = AreaKalmanFilter()
                        area_kf.update(area)
                        okt = True
        else:
            # Modo seguimiento CSRT + Kalman
            ok, raw_bbox = tracker.update(frm)
            if ok:
                # Suavizar área con Kalman
                raw_area = raw_bbox[2] * raw_bbox[3]
                smoothed_area = area_kf.update(raw_area)
                
                # Ajuste proporcional del bbox
                scale_factor = np.sqrt(smoothed_area / raw_area) if raw_area > 0 else 1.0
                adj_w = int(raw_bbox[2] * scale_factor)
                adj_h = int(raw_bbox[3] * scale_factor)
                adj_bbox = (raw_bbox[0], raw_bbox[1], adj_w, adj_h)
                
                # Dibujado y lógica de transición
                p1 = (int(adj_bbox[0]), int(adj_bbox[1]))
                p2 = (int(adj_bbox[0]+adj_bbox[2]), int(adj_bbox[1]+adj_bbox[3]))
                cv2.rectangle(frm, p1, p2, (0,255,0), 2)
                cv2.putText(frm, f'Area: {int(smoothed_area)}', (p1[0], p1[1]-20), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                
                if smoothed_area > (AREA_THRESHOLD + HYSTERESIS):
                    okt = False
            else:
                okt = False
        
        cv2.imshow('CSRT + Kalman Area Adjustment', frm)
        if cv2.waitKey(1) == 27:
            break

cam.release()
cv2.destroyAllWindows()