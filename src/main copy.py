# Programa que para detectar y coordinar dron mediante el rostro detectado
import cv2
import time
import numpy as np
import math
import threading
from simple_pid import PID
from pymavlink import mavutil

# pid
dist_pid = PID(0.3,0.001,0.01,20,0.5,output_limits=(-3,3))
yaw_pid = PID(0.1,0.001,0.01,0,0.5,output_limits=(-3,3))

heading = 0  # Variable global para el heading
def get_heading_thread(dron):
    global heading
    while True:
        try:
            msg = dron.recv_match(type='VFR_HUD', blocking=True, timeout=1)
            if msg is not None:
                heading = msg.heading
                print(f"[Thread] Heading: {heading}")
        except Exception as e:
            print(f"[Thread] Error getting heading: {e}")
        time.sleep(0.1)  # Consulta cada 100 ms

# camara
cam = cv2.VideoCapture(0)

# Detección con OpenCV DNN (Caffe)
net = cv2.dnn.readNetFromCaffe("complementos/modelos/deploy.prototxt", "complementos/modelos/res10_300x300_ssd_iter_140000_fp16.caffemodel")
in_width = 300
in_height = 300
mean = [104, 117, 123]
conf_threshold = 0.7

trackers = ['KCF', 'MOSSE', 'CSRT']
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
    dron = mavutil.mavlink_connection('udpin:localhost:14550')
except Exception as e:
    print("Error connecting to the vehicle: ", e)
    exit(1)

dron.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (dron.target_system, dron.target_component))

dron.mav.set_mode_send(
    dron.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    4 # 4 = GUIDED
)
# armar
dron.mav.command_long_send(
    dron.target_system,
    dron.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    1,0,0,0,0,0,0
)
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
msg = dron.recv_match(type='COMMAND_ACK',blocking=True)
print('despegue cmd', msg.result)
time.sleep(5)
okt = False

def rot_x(theta):
    return np.array([
        [1, 0, 0],
        [0, np.cos(theta), -np.sin(theta)],
        [0, np.sin(theta), np.cos(theta)]
    ])

def rot_y(theta):
    return np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])

def rot_z(theta):
    return np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0],
        [0, 0, 1]
    ])

while True:
    ok, frm = cam.read()
    if not ok:
        print('Error')
        break
    #frm = cv2.flip(frm,1)
    if not okt:
        # Detección de caras con OpenCV DNN (Caffe)
        frame_height = frm.shape[0]
        frame_width = frm.shape[1]
        blob = cv2.dnn.blobFromImage(frm, 1.0, (in_width, in_height), mean, swapRB=False, crop=False)
        net.setInput(blob)
        detections = net.forward()
        bbox = None
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_threshold:
                x_top_left = int(detections[0, 0, i, 3] * frame_width)
                y_top_left = int(detections[0, 0, i, 4] * frame_height)
                x_bottom_right = int(detections[0, 0, i, 5] * frame_width)
                y_bottom_right = int(detections[0, 0, i, 6] * frame_height)
                bbox = (x_top_left, y_top_left, x_bottom_right - x_top_left, y_bottom_right - y_top_left)
                break

        if bbox:
            he, wi = frm.shape[:2]
            xc = bbox[0] + bbox[2] // 2 - wi // 2
            yc = bbox[1] + bbox[3] // 2 - he // 2
            p1 = int(bbox[0]), int(bbox[1])
            p2 = int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3])
            cv2.rectangle(frm, p1, p2, (255, 0, 0), 2)
            cv2.putText(frm, str(bbox[2]*bbox[3]), (p1[0], p1[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            #if (bbox[2] * bbox[3]) < 10000:
                #tracker.init(frm, bbox)
                #okt = True
            a = bbox[2] * bbox[3]
            vx, vy, vz = dist_pid(a/1000), yaw_pid(xc), 0
            if a < 0:
                an = -90
            else:
                an = 0

            v = np.array([vx, vy, vz])
            rot = np.diag([1,-1,-1])*rot_z(math.degrees(heading))*rot_y(0)*rot_x(0)
            vp = np.dot(rot, v)
            print(vp)
            dron.mav.set_position_target_local_ned_send(
                0,
                dron.target_system,
                dron.target_component,
                mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                2503, # solo posicion
                0,0,0,
                vp[0],vp[1],0,
                0,0,0,
                0,0
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