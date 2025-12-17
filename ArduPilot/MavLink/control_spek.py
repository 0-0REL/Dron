# comprobar com se comporta el control
# no funciona, bloquea la lectura del receptor

import time
import threading
from pymavlink import mavutil

try:
    radio = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600) # ACM dron USB telemetría
except Exception as e:
    print("Error connecting to the vehicle: ", e)
    exit(1)

radio.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (radio.target_system, radio.target_component))

spektrum = False
def regreso_control():
    while True:
        global spektrum
        canales = radio.recv_match(type='RC_CHANNELS_RAW',blocking=True)
        print('valor de canal de modos de vuelo: %s' % canales.chan5_raw)
        if canales.chan5_raw == 1128: # cambiar a STABILIZE
            print('Regresando al control manual')
            spelktrum = True

# apagar motores y poner en modo 'GUIDED'
guided = 1926
radio.mav.rc_channels_override_send(
    radio.target_system,
    radio.target_component,
    1500,  # channel 1
    1500,  # channel 2
    1000,  # channel 3
    1500,  # channel 4
    guided,  # channel 5 poner en modo 'GUIDED'
    1500,  # channel 6
    1500,  # channel 7
    1500   # channel 8
)

cont_rc = threading.Thread(target=regreso_control, daemon=True)
cont_rc.start()

while spektrum is False:
    print('Moviendo hacia adelante (3 segundos)...')
    for i in range(3):
        radio.mav.rc_channels_override_send(
            radio.target_system,
            radio.target_component,
            1500,  # channel 1
            1700,  # channel 2 moviendo adelante
            1500,  # channel 3
            1000,  # channel 4
            guided,  # channel 5
            1500,  # channel 6
            1500,  # channel 7
            1500   # channel 8
        )
        time.sleep(1)
    print('Moviendo hacia atras (3 segundos)...')
    for i in range(3):
        radio.mav.rc_channels_override_send(
            radio.target_system,
            radio.target_component,
            1500,  # channel 1
            1200,  # channel 2 moviendo atras
            1500,  # channel 3
            1000,  # channel 4
            guided,  # channel 5
            1500,  # channel 6
            1500,  # channel 7
            1500   # channel 8
        )
        time.sleep(1)
    print('Moviendo hacia derecha (3 segundos)...')
    for i in range(3):
        radio.mav.rc_channels_override_send(
            radio.target_system,
            radio.target_component,
            1700,  # channel 1 a la derecha
            1500,  # channel 2
            1500,  # channel 3
            1000,  # channel 4
            guided,  # channel 5
            1500,  # channel 6
            1500,  # channel 7
            1500   # channel 8
        )
        time.sleep(1)
    print('Moviendo hacia izquierda (3 segundos)...')
    for i in range(3):
        radio.mav.rc_channels_override_send(
            radio.target_system,
            radio.target_component,
            1200,  # channel 1 moviendo a la izquierda
            1500,  # channel 2
            1500,  # channel 3
            1000,  # channel 4
            guided,  # channel 5
            1500,  # channel 6
            1500,  # channel 7
            1500   # channel 8
        )
        time.sleep(1)