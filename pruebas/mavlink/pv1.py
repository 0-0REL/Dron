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

def mov_dron(roll: int = 64035, pitch: int = 64035, throttle: int = 64035, yaw: int = 64035):
    """control de rc
    valores de -500 a 500"""
    #65535
    dron_conec.mav.rc_channels_override_send(
        dron_conec.target_system,
        dron_conec.target_component,
        int(1500+roll), int(1500+pitch), int(1500+throttle), int(1500+yaw), 65535, 65535, 65535, 65535
    )

def auto_despegue(alt: float = 1.0):
    """Auto despegue a una altitud específica"""
    print('despega')
    dron_conec.mav.command_long_send(
        dron_conec.target_system,
        dron_conec.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,
        0, 0, 0, 0, 0, 0, alt
    )
    # checar cmd despegue
    msg = dron_conec.recv_match(type='COMMAND_ACK', blocking=True)
    if msg.result == 0:
        msg = dron_conec.recv_match(type='VFR_HUD', blocking=True)
        while msg.alt < alt and not break_program:
            msg = dron_conec.recv_match(type='VFR_HUD', blocking=True)
            print(f"Altura: {msg.alt:.2f}m",end='\r')

def despegue(altura: float):
    ctrl_rll.setpoint = 0
    ctrl_ptch.setpoint = 0
    ctrl_thr.setpoint = altura
    while True is not break_program:
        vfr_hud = dron_conec.recv_match(type='VFR_HUD', blocking=True)
        if vfr_hud.alt > altura:
            break
        att = dron_conec.recv_match(type='ATTITUDE', blocking=True)
        mov_dron(int(ctrl_rll(att.roll)), int(ctrl_ptch(att.pitch)), int(ctrl_thr(vfr_hud.alt)))
        print(f"alt: {vfr_hud.alt}", end='\r')
def mod_vuelo(mod:int = 1228):
    """Modo de vuelo
    guided 1926
    alhold 1526
    stabilize 1128
    """
    dron_conec.mav.rc_channels_override_send(
        dron_conec.target_system,
        dron_conec.target_component,
        1500, 1500, 1000, 1500, mod, 1000, 1000, 1000
    )

# Configuración del PID
ctrl_thr = PID(15, 5, 8, output_limits=(-500, 500))
ctrl_ptch = PID(10, 2, 5, output_limits=(-500, 500))
ctrl_rll = PID(10, 2, 5, output_limits=(-500, 500))

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
mod_vuelo(1128)

# Armar el dron
armar()
despegue(1)
# Bucle principal de control
ctrl_thr.setpoint = 1  # 1 metro de altitud objetivo

try:
    print("")
    while not break_program:
        msg = dron_conec.recv_match(type='VFR_HUD', blocking=True)
        if msg:
            alt = msg.alt
            thr = ctrl_thr(alt)
            #if alt < ctrl_thr.setpoint:
            mov_dron(pitch=100,throttle=int(thr))
            #else:
            #    mov_dron(pitch=1600,throttle=int(1500 - thr))
            
            rc_data = dron_conec.recv_match(type='RC_CHANNELS_RAW', blocking=True)
            if rc_data:
                print(f"Altura: {alt:.2f}m | RC3: {rc_data.chan3_raw} RC3: {rc_data.chan2_raw}", end='\r')

finally:
    mov_dron(0, 0, -200, 0)
    t1 = time.time()
    print('\nbaja 5seg')
    while time.time() - t1 < 5:
        pass
    # Secuencia de terminación (siempre se ejecuta)
    mov_dron(throttle=-500)  # Throttle mínimo
    dron_conec.close()
    listener.stop()  # Detener el listener de teclado
    print('fin')