# con los comando de modo guiado
import numpy as np
import math
import time
from pymavlink import mavutil

def R01(yaw:float, p:np.array=[0,0,0]) -> np.array:
    r = np.array([[math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), 0],
               [math.sin(math.radians(yaw)), -math.cos(math.radians(yaw)), 0],
               [0,0,-1]])
    return np.dot(r,p)

# Start a connection listening on a UDP port
try:
    #dron = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
    #dron = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
    dron = mavutil.mavlink_connection('udpin:localhost:14550')
except Exception as e:
    print("Error connecting to the vehicle: ", e)
    exit(1)
# Wait for the first heartbeat to set the system and component ID of remote system for the link
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
    0,0,0,0,0,0,10
)
# checar cmd despegue
msg = dron.recv_match(type='COMMAND_ACK',blocking=True)
print('despegue cmd', msg.result)
time.sleep(5)

print('se va')
p = R01(0, np.array([100,0,10]))
print(p)
dron.mav.set_position_target_local_ned_send(
    0,
    dron.target_system,
    dron.target_component,
    mavutil.mavlink.MAV_FRAME_LOCAL_NED,
    3520,
    p[0],p[1],p[2],
    0.5,0.5,0.5,
    0,0,0,
    0,0
)
time.sleep(15)
# aterrizaje
dron.mav.command_long_send(
    dron.target_system,
    dron.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LAND,
    0,
    0,0,0,0,0,0,10
)