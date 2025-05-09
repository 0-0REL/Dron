from simple_pid import PID
from pymavlink import mavutil
import time

al = PID(0.5,0,0,1, output_limits=(1000,2000))
# conectar
try:
    dron_conec = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
    #dron_conec = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
    #dron_conec = mavutil.mavlink_connection('udpin:localhost:14550')
except Exception as e:
    print("Error connecting to the vehicle: ", e)
    exit(1)
dron_conec.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (dron_conec.target_system, dron_conec.target_component))

msg = dron_conec.recv_match(type='VFR_HUD',blocking=True)

while True:
    if msg.alt < 1:
        msg = dron_conec.recv_match(type='VFR_HUD',blocking=True)
        print('altura:',msg.alt)
        thr = al(msg.alt)
        print('rc:',thr)