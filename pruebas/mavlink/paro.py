from pymavlink import mavutil
from simple_pid import PID
import time
from pynput import keyboard

# Variable global para controlar la interrupción
break_program = False

def on_press(key):
    """Callback para detectar teclas presionadas"""
    global break_program
    try:
        if key == keyboard.Key.esc:  # Detectar tecla ESC
            break_program = True
            return False  # Detiene el listener
    except AttributeError:
        pass

# Configurar el listener de teclado en segundo plano
listener = keyboard.Listener(on_press=on_press)
listener.start()

def armar(arm: int = 1):
    """Armar dron"""
    dron_conec.mav.command_long_send(
        dron_conec.target_system,
        dron_conec.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        arm, 0, 0, 0, 0, 0, 0
    )
    # checar armado
    msg = dron_conec.recv_match(type='COMMAND_ACK', blocking=True)
    if msg.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print('Fallo en armar:', msg.result)
        exit(1)
    print('Armado')
    time.sleep(3)

def mov_dron(roll: int = 65535, pitch: int = 65535, throttle: int = 65535, yaw: int = 65535):
    """control de rc"""
    dron_conec.mav.rc_channels_override_send(
        dron_conec.target_system,
        dron_conec.target_component,
        roll, pitch, throttle, yaw, 65535, 65535, 65535, 65535
    )

# Configuración del PID
ctrl_thr = PID(15, 5, 8, output_limits=(1.1e3, 2e3))

# Conectar al dron
try:
    dron_conec = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
except Exception as e:
    print("Error connecting to the vehicle: ", e)
    exit(1)

# Esperar heartbeat
dron_conec.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (dron_conec.target_system, dron_conec.target_component))

# Configuración inicial
dron_conec.mav.rc_channels_override_send(
    dron_conec.target_system,
    dron_conec.target_component,
    1500, 1500, 1000, 1500, 1128, 1000, 1000, 1000
)

# Armar el dron
armar()

# Bucle principal de control
ctrl_thr.setpoint = 1  # 1 metro de altitud objetivo

try:
    while not break_program:
        msg = dron_conec.recv_match(type='VFR_HUD', blocking=True)
        if msg:
            alt = msg.alt
            thr = ctrl_thr(alt)
            mov_dron(throttle=int(thr))
            
            rc_data = dron_conec.recv_match(type='RC_CHANNELS_RAW', blocking=True)
            if rc_data:
                print(f"Altura: {alt:.2f}m | RC3: {rc_data.chan3_raw}", end='\r')

finally:
    # Secuencia de terminación (siempre se ejecuta)
    mov_dron(throttle=1000)  # Throttle mínimo
    dron_conec.mav.command_long_send(
        dron_conec.target_system,
        dron_conec.target_component,
        mavutil.mavlink.MAV_CMD_DO_FLIGHTTERMINATION,
        0,
        1, 0, 0, 0, 0, 0, 0
    )
    dron_conec.close()
    listener.stop()  # Detener el listener de teclado
    print('fin')