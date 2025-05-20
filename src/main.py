# Programa que para detectar y coordinar dron mediante el rostro detectado
import mediapipe as mp
import cv2
import time
import numpy as np
import math
from simple_pid import PID
from pymavlink import mavutil

# pid
dist_pid = PID(0.3,0.001,0.01,15,0.5,output_limits=(-3,3))

# camara
cam = cv2.VideoCapture(0)

# configuraciones del mediapipe
DETECTION_RESULT = None
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

try:
    #dron = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
    #dron = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
    dron = mavutil.mavlink_connection('udpin:localhost:14550')
except Exception as e:
    print("Error connecting to the vehicle: ", e)
    exit(1)

dron.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (dron.target_system, dron.target_component))
dron.set_mode_apm(mode='GUIDED')
# armar
dron.mav.command_long_send(
    dron.target_system,
    dron.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    1,0,0,0,0,0,0
)
# checar armado
msg = dron.recv_match(type='COMMAND_ACK',blocking=True)
if msg.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
    print('Fallo en armar:', msg.result)
    exit(1)
print('Armado')
time.sleep(1)

# auto despegue a 1 m
dron.mav.command_long_send(
    dron.target_system,
    dron.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0,
    0,0,0,0,0,0,1
)
# checar cmd despegue
msg = dron.recv_match(type='COMMAND_ACK',blocking=True)
print('despegue cmd', msg.result)
time.sleep(5)
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
                    #cv2.circle(frm, (bbox[0]+bbox[2]//2, bbox[1]+bbox[3]//2), 5, (0,0,255),-1)
                    p1 = int(bbox[0]), int(bbox[1])
                    p2 = int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3])
                    cv2.rectangle(frm, p1, p2, (255, 0, 0), 2)
                    cv2.putText(frm, str(bbox[2]*bbox[3]), (p1[0], p1[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    #if (bbox[2] * bbox[3]) < 10000:
                        #tracker.init(frm, bbox)
                        #okt = True
                    a = bbox[2] * bbox[3]
                    vx = dist_pid(a/1000)
                    if a < 0:
                        an = -90
                    else:
                        an = 0
                    print(vx)
                    dron.mav.set_position_target_local_ned_send(
                    0,
                    dron.target_system,
                    dron.target_component,
                    mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                    2503, # solo posicion
                    0,0,0,
                    vx,0,0,
                    0,0,0,
                    math.radians(an),0
                    )
                else:
                    dron.mav.set_position_target_local_ned_send(
                    0,
                    dron.target_system,
                    dron.target_component,
                    mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                    2503, # solo posicion
                    0,0,0,
                    0,0,0,
                    0,0,0,
                    0,0
                    )
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
# regresar a casa
dron.mav.command_long_send(
    dron.target_system,
    dron.target_component,
    mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
    0,
    0,0,0,0,0,0,0
)