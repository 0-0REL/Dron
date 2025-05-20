# despegeue y aterrizaje

from pymavlink import mavutil
import time
import sys
from pynput import keyboard

def press_esc(key):
    """Callback para detectar teclas presionadas"""
    try:
        if key == keyboard.Key.esc:  # Detectar tecla ESC
            
            return False  # Detiene el listener
    except AttributeError:
        pass

# Configurar el listener de teclado en segundo plano
listener = keyboard.Listener(on_press=press_esc)
listener.start()

# establecer conexion
try:
    dron = mavutil.mavlink_connection('udpin:localhost:14550')
except:
    print('no se pudo conectar')
    sys.exit()
# esperar primer latido
dron.wait_heartbeat()

# establecer casa
dron.mav.command_init_send(
    dron.target_system,
    dron.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_HOME,
    0,
    0,
    1,0,0,0,0,0,0
)

# establecer modo
dron.set_mode_apm(mode='GUIDED')

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
    sys.exit()
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
while True:
    msg = dron.recv_match(type='VFR_HUD', blocking=True)
    if msg.alt > 1:
        print('despego')
        break # se llego a 1 m
# esperar 3 segundos
time.sleep(3)

# aterizar
dron.mav.command_long_send(
    dron.target_system,
    dron.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LAND,
    0,
    0,0,0,0,0,0,1
)
print('aterrizando')