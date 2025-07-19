""" Simulacion con pymavlink y control de rc
"""
import time
import simple_mav as smav
from simple_pid import PID

# objetos
uav = smav.SimpleMav(4) # 0 estabilizar, 1 acro

thro_pid = PID(0.6, 0.05, 0.01, output_limits=(0, 1))
pth_pid = PID(0, 0, 0, sample_time=0.2, output_limits=(-0.5, 0.5))
yaw_pid = PID(0, 0, 0, sample_time=0.2, output_limits=(-0.5, 0.5))

# configuraciones
#uav.intervalo_msg('VFR_HUD', 30) # 50 Hz
#uav.intervalo_msg('ATTITUDE', 30) # 50 Hz
#uav.intervalo_msg('RC_CHANNELS', 30) # 50 Hz

# inicio
uav.armar(1)
time.sleep(5)
#alt_ini = uav.recibir_msg('VFR_HUD').alt
#print(f"Altura inicial: {alt_ini:.2f} m")
#altura = 0
#thro_pid.setpoint = 1
uav.modov(0)
while True:
    pass
    #thr = int(thro_pid(altura)*1000) # Control de throttle
    uav.rc_control(1600, Throttle=1530)
    #altu = uav.recibir_msg('VFR_HUD')
    #if altu is None:
    #    continue
    #altura = altu.alt - alt_ini
    #print(f"Altura: {altura:.2f} m, {thr:.2f}")