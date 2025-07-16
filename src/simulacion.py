""" Simulacion con pymavlink y control de rc
"""

import cv2
import math
import time
import simple_mav as smav
from simple_pid import PID

# objetos
uav = smav.SimpleMav(0) # 0 estabilizar, 1 acro

thro_pid = PID(100, 100, 50, output_limits=(1000, 2000))
pth_pid = PID(0.5, 0, 0, sample_time=0.2, output_limits=(-500, 500))
yaw_pid = PID(0.5, 0, 0, sample_time=0.2, output_limits=(-500, 500))

# configuraciones
uav.intervalo_msg('VFR_HUD', 30) # 50 Hz
uav.intervalo_msg('ATTITUDE', 30) # 50 Hz

# inicio
uav.armar(1)
time.sleep(3)
alt_ini = uav.recibir_msg('VFR_HUD').alt
print(f"Altura inicial: {alt_ini:.2f} m")
altura = 0
thro_pid.setpoint = 1
while True:
    thr = int(thro_pid(altura)) # Control de throttle
    uav.rc_control(Throttle=thr)
    altura = uav.recibir_msg('VFR_HUD').alt - alt_ini
    print(f"Altura: {altura:.2f} m, {thr:.2f}")