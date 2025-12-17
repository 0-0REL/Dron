from simple_pid import PID
from pymavlink import mavutil
import time
#import keyboard

altura_ctrl = PID(0.5, 0, 0.2, sample_time=0.2, output_limits=(1e3, 2e3))
# conectar
try:
    #dron_conec = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
    dron_conec = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
    #dron_conec = mavutil.mavlink_connection('udpin:localhost:14550')
except Exception as e:
    print("Error connecting to the vehicle: ", e)
    exit(1)
dron_conec.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (dron_conec.target_system, dron_conec.target_component))

def fin():
    dron_conec.mav.command_long_send(
    dron_conec.target_system,
    dron_conec.target_component,
    mavutil.mavlink.MAV_CMD_DO_FLIGHTTERMINATION,
    0,
    1,0,0,0,0,0,0
    )
    exit(1)

#keyboard.on_press_key('q', lambda _: fin())

#dron_conec.set_mode_apm(mode='GUIDED')
dron_conec.mav.rc_channels_override_send(
            dron_conec.target_system,
            dron_conec.target_component,
            1500,1500,1000,1500,1128,1000,1000,1000
        )
# armar
dron_conec.mav.command_long_send(
    dron_conec.target_system,
    dron_conec.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    1,0,0,0,0,0,0
)
# checar armado
msg = dron_conec.recv_match(type='COMMAND_ACK',blocking=True)
if msg.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
    print('Fallo en armar:', msg.result)
    exit(1)
print('Armado')
time.sleep(2)
# elevar
while True:
    msg = dron_conec.recv_match(type='VFR_HUD',blocking=True)
    print(msg.alt)
    #altura_ctrl.setpoint = 1 # subir un metro
    #while msg.alt < 1:
    #msg = dron_conec.recv_match(type='VFR_HUD',blocking=True)
    dron_conec.mav.manual_control_send(
    dron_conec.target_system,
    500,-500,250,500,0
    )
    msg = dron_conec.recv_match(type='RC_CHANNELS_RAW', blocking=True, timeout=1)
    print('chan3:', msg.chan3_raw)