# prueba de modo automático
# rutina de prueba: depega, acelera y aterriza
# resultado: no despega, modificacion de canales responde correctamente, land no funciono

from pymavlink import mavutil
import time

# conexion con simulador ardupilot, usa udp
try:
    dron_conec = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
except Exception as e:
    print("Error connecting to the vehicle: ", e)
    exit(1)

# Espera el primer latido para establecer el sistema y el componente del sistema remoto para el enlace
dron_conec.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (dron_conec.target_system, dron_conec.target_component))

# apagar motores y poner en modo 'GUIDED'

# Mostrar valor de modo de vuelo
msg = dron_conec.recv_match(type='RC_CHANNELS_RAW',blocking=True)
print('valor de canal de modos de vuelo: %s' % msg.chan5_raw)
# armar
print('armando...')
dron_conec.mav.command_long_send(
    dron_conec.target_system,
    dron_conec.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    1,
    0,
    0,
    0,
    0,
    0,
    0
)
msg = dron_conec.recv_match(type='COMMAND_ACK',blocking=True)
print(msg)
# despegar
print('despege')
dron_conec.mav.command_long_send(
    dron_conec.target_system,
    dron_conec.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0,  # confirmation
    0,  # param1: min pitch
    0,  # param2: empty
    0,  # param3: empty
    0,  # param4: yaw
    0,  # param5: latitude
    0,  # param6: longitude
    1, # param7: altitude
)
msg = dron_conec.recv_match(type='COMMAND_ACK',blocking=True)
print(msg)
time.sleep(5) # despega, 5 segundos
# subir
print('sube')
dron_conec.mav.rc_channels_override_send(
    dron_conec.target_system,
    dron_conec.target_component,
    1500,  # channel 1
    1500,  # channel 2
    1700,  # channel 3 acelera
    1500,  # channel 4
    1500,  # channel 5
    1500,  # channel 6
    1000,  # channel 7
    1000   # channel 8
)
time.sleep(5)
# mantener altura
print('matiene altura')
dron_conec.mav.rc_channels_override_send(
    dron_conec.target_system,
    dron_conec.target_component,
    2000,  # channel 1
    1500,  # channel 2
    1000,  # channel 3 acelera
    1500,  # channel 4
    1500,  # channel 5
    1500,  # channel 6
    1000,  # channel 7
    1000   # channel 8
)
time.sleep(5)
# aterrizar
print("Aterrizando...")
dron_conec.mav.command_long_send(
    dron_conec.target_system,
    dron_conec.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LAND,
    0,  # confirmation
    0,  # param1: min pitch
    0,  # param2: empty
    0,  # param3: empty
    0,  # param4: yaw
    0,  # param5: latitude
    0,  # param6: longitude
    1, # param7: altitude
)
print('aterrizo')
time.sleep(5)
# Desconectar
dron_conec.close()
print("Desconectado del vehículo.")
# Fin de la rutina