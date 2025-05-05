# seguiemito con mediapipe y CSRT
# mediapipe para deteccion y CSRT como seguidor
import mediapipe as mp
import cv2
import time

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

def bbox_mp(detecciones):
    """bbox detectado por mediapipe
    Args:
        detection_result: The list of all "Detection" entities to be visualized.
    Returns:
        bounding boxes.
    """
    if not detecciones.detections:
        return None
    #for detection in detecciones.detections:
        # Draw bounding_box
        #detection.bounding_box
    bbox = detecciones.detections[0].bounding_box     
    return (int(bbox.origin_x), int(bbox.origin_y), int(bbox.width), int(bbox.height))

options = FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path='src/blaze_face_short_range.tflite'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

trackers = ['KCF', 'MOSSE', 'CSRT']
# knf recomendado por tutorial
# mosse maso
# csrt casi perfecto
tcker = trackers[2]
if tcker == 'KCF':
    trak = cv2.TrackerKCF_create()
elif tcker == 'MOSSE':
    trak = cv2.legacy.TrackerMOSSE_create()
elif tcker == 'CSRT':
    trak = cv2.TrackerCSRT_create()
else:
    print('Error: tracker not found')
    exit(1)
tracker = trak

okt = False
with FaceDetector.create_from_options(options) as detector:
    while True:
        ok, frm = cam.read()
        if not ok:
            print('Error')
            break
        frm = cv2.flip(frm, 1)
        if not okt:
            # deteccion de caras con mediapipe
            frm_rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frm_rgb)
            detector.detect_async(mp_image, time.time_ns() // 1_000_000)
            if DETECTION_RESULT:
                bbox = bbox_mp(DETECTION_RESULT)
                if bbox:
                    cv2.circle(frm, (bbox[0]+bbox[2]//2, bbox[1]+bbox[3]//2), 5, (0,0,255),-1)
                    if (bbox[2] * bbox[3]) < 10000:
                        tracker.init(frm, bbox)
                        okt = True
        else:
            #seguidor
            ok, bbox = tracker.update(frm)
            if ok:
                p1 = int(bbox[0]), int(bbox[1])
                p2 = int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3])
                cv2.rectangle(frm, p1, p2, (255, 0, 0), 2)
                cv2.putText(frm, str(bbox[2]*bbox[3]), (p1[0], p1[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                if bbox[2]*bbox[3] > 9500:
                    okt = False
                    del tracker
                    tracker = trak
            else:
                #cv2.putText(frm, 'Lost', (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                okt = False
        cv2.imshow('face_detection', frm)
        # Stop the program if the ESC key is pressed.
        if cv2.waitKey(1) == 27:
                    break
        
cam.release()
cv2.destroyAllWindows()