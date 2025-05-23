# despegeue y aterrizaje

from pymavlink import mavutil
import time
import sys
from pynput import keyboard

ESC_PRESSED = False
def press_esc(key):
    """Callback para detectar teclas presionadas"""
    global ESC_PRESSED
    try:
        if key == keyboard.Key.esc:  # Detectar tecla ESC
            ESC_PRESSED = True
            return False  # Detiene el listener
    except AttributeError:
        pass
    return False

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
#dron.mav.command_init_send(
#    dron.target_system,
#    dron.target_component,
#    mavutil.mavlink.MAV_CMD_DO_SET_HOME,
#    0,
#    0,
#    1,0,0,0,0,0,0
#)

# establecer modo
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
print(msg.result)
if msg.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
    print('Fallo en armar:', msg.result)
    sys.exit()
print('Armado')
time.sleep(5)

# auto despegue a 1 m
dron.mav.command_long_send(
    dron.target_system,
    dron.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0,
    0,0,0,0,0,0,0.5
)
while True:
    msg = dron.recv_match(type='VFR_HUD', blocking=True)
    #print(msg.alt)
    if msg.alt > 0.5:
        print('despego')
        break # se llego a 1 m
# esperar 3 segundos
time.sleep(6)

# aterizar
dron.mav.command_long_send(
    dron.target_system,
    dron.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LAND,
    0,
    0,0,0,0,0,0,0.5
)
print('aterrizando')
while True:
    if ESC_PRESSED:
        print('fin')
        dron.mav.command_long_send(
        dron.target_system,
        dron.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        0,21196,0,0,0,0,0
        )
        break

dron.close()