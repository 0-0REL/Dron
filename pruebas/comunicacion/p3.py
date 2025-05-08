# prueba 3
# salir e inciar el gps, guided lo ocupa
# probar desde telemtria

from pymavlink import mavutil
import time

# conectar
try:
    #dron_conec = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
    #dron_conec = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
    dron_conec = mavutil.mavlink_connection('udpin:localhost:14550')
except Exception as e:
    print("Error connecting to the vehicle: ", e)
    exit(1)

# Espera el primer latido para establecer el sistema y el componente del sistema remoto para el enlace
dron_conec.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (dron_conec.target_system, dron_conec.target_component))

dron_conec.set_mode_apm(mode='GUIDED')
# modos
    # guided 1926
    # alhold 1526
    # stabilize 1128
#dron_conec.mav.rc_channels_override_send(
#            dron_conec.target_system,
#            dron_conec.target_component,
#            1500,1500,1000,1500,1128,1000,1000,1000
#        )
#msg = dron_conec.recv_match(type='RC_CHANNELS_RAW',blocking=True)
#print('valor de canal 5: %s' % msg.chan5_raw)
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
time.sleep(3)

# auto despegue a 1 m
dron_conec.mav.command_long_send(
    dron_conec.target_system,
    dron_conec.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0,
    0,0,0,0,0,0,1
)
# checar cmd despegue
msg = dron_conec.recv_match(type='COMMAND_ACK',blocking=True)
print('despegue cmd', msg.result)
time.sleep(5)

# aterrizaje
dron_conec.mav.command_long_send(
    dron_conec.target_system,
    dron_conec.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LAND,
    0,
    0,0,0,0,0,0,1
)
# checar cmd aterrizaje
msg = dron_conec.recv_match(type='COMMAND_ACK',blocking=True)
print('aterizaje cmd:', msg.result)

# desarmar 
dron_conec.mav.command_long_send(
    dron_conec.target_system,
    dron_conec.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    0,1,0,0,0,0,0
)

print("Desconectado del vehículo.")
dron_conec.close()