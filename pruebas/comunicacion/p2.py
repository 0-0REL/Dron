# prueba 2
# mover roll, pitch, throttle, yaw
# auto despegue pendiente

import time
from pymavlink import mavutil

# conectar a dron
try:
    #dron_conec = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
    dron_conec = mavutil.mavlink_connection('udpin:localhost:14550')
except Exception as e:
    print("Error connecting to the vehicle: ", e)
    exit(1)

# esperar a conexion
dron_conec.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (dron_conec.target_system, dron_conec.target_component))

mode_id = dron_conec.mode_mapping()["GUIDED"]
print(mode_id)
dron_conec.mav.command_long_send(
    dron_conec.target_system,
    dron_conec.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_MODE,
    0,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id, 0, 0, 0, 0, 0
)
#msg = dron_conec.recv_match(type='RC_CHANNELS_RAW',blocking=True)
#print('valor de canal 5: %s' % msg.chan5_raw)
# armar dron
dron_conec.mav.command_long_send(
    dron_conec.target_system,
    dron_conec.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    1,0,0,0,0,0,0
)
# comprobrar armado
msg = dron_conec.recv_match(type='COMMAND_ACK', blocking=True)
if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
    print('ARMADO')
else:
    print('armar ack:',msg.result)
    exit(1)

# despegue
dron_conec.mav.command_long_send(
    dron_conec.target_system,
    dron_conec.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0,
    0,0,0,0,0,0,1, # param7: altitude
)
msg = dron_conec.recv_match(type='COMMAND_ACK',blocking=True)
if msg.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
    print('fallo take of')
mov = [1500, 1500, 1000, 1500]
f = []
for ch in range(4):
    while True:
        if mov[ch] == 2000 and ch == 2:
            mov[ch] == 1000
            f = True
        elif mov[ch] == 2000:
            mov[ch] == 1500
            f = True
        dron_conec.mav.rc_channels_override_send(
            dron_conec.target_system,
            dron_conec.target_component,
            int(mov[0]),int(mov[1]),int(mov[2]),int(mov[3]),1926,1000,1000,1000
        )
        if f:
            f = False
            break
        mov[ch] += 100
        time.sleep(1)
        msg = dron_conec.recv_match(type='RC_CHANNELS_RAW', blocking=False)
        try:
            print(msg.chan1_raw,msg.chan2_raw,msg.chan3_raw,msg.chan4_raw)
        except Exception:
            print(Exception)