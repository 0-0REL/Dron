# prueba de modo automático
# rutina de prueba: arriba, abajo, izquierda, derecha

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
dron_conec.mav.rc_channels_override_send(
    dron_conec.target_system,
    dron_conec.target_component,
    1000,  # channel 1
    1000,  # channel 2
    1000,  # channel 3
    1000,  # channel 4
    1926,  # channel 5 poner en modo 'GUIDED' < revisar valor
    1000,  # channel 6
    1000,  # channel 7
    1000   # channel 8
)
# mostrar valores de los canales
msg = dron_conec.recv_match(type='RC_CHANNELS_RAW',blocking=True)
print('valor de canal de modos de vuelo: %s' % msg.chan5_raw)

# despegar
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
# mover hacia adelante modificando el canal 3
dron_conec.mav.rc_channels_override_send(
    dron_conec.target_system,
    dron_conec.target_component,
    1000,  # channel 1
    1000,  # channel 2
    1500,  # channel 3
    1000,  # channel 4
    1500,  # channel 5
    1000,  # channel 6
    1000,  # channel 7
    1000   # channel 8
)
# leer valo del canar 3 por 3 segundos
for i in range(3):
    msg = dron_conec.recv_match(type='RC_CHANNELS_RAW',blocking=True)
    print('valor de canal 3: %s' % msg.chan3_raw)
    time.sleep(1)

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
# leer valo del canar 3 por 3 segundos
for i in range(3):
    msg = dron_conec.recv_match(type='RC_CHANNELS_RAW',blocking=True)
    print('valor de canal 3: %s' % msg.chan3_raw)
    time.sleep(1)

# Desconectar
dron_conec.close()
print("Desconectado del vehículo.")
# Fin de la rutina