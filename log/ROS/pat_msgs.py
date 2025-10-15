import pandas as pd
import re

# Leer CSV filtrado
df = pd.read_csv("/home/rodrigo/Descargas/02rosout01-10.csv")

# Crear listas para guardar los datos
timestamps_pwm = []
pwm_values = []
timestamps_orient = []
orient_values = []
timestamps_pid = []
pid_values = []

# Regex para extraer números
pwm_pattern = re.compile(r"Mot_PWM:\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
orient_pattern = re.compile(r"Orientacion:\s*roll\s*=\s*([-+]?\d*\.?\d+),\s*pitch\s*=\s*([-+]?\d*\.?\d+),\s*yaw\s*=\s*([-+]?\d*\.?\d+)")
pid_pattern = re.compile(r"cR:\s*([-+]?\d*\.?\d+),\s*cP:\s*([-+]?\d*\.?\d+),\s*cY:\s*([-+]?\d*\.?\d+)")

for index, row in df.iterrows():
    msg = str(row['message'])
    ts = row['timestamp']
    
    # Buscar mensajes PWM
    pwm_match = pwm_pattern.search(msg)
    if pwm_match:
        timestamps_pwm.append(ts)
        pwm_values.append([int(pwm_match.group(1)), int(pwm_match.group(2)), int(pwm_match.group(3)), int(pwm_match.group(4))])
    
    # Buscar mensajes de Orientación
    orient_match = orient_pattern.search(msg)
    if orient_match:
        timestamps_orient.append(ts)
        orient_values.append([float(orient_match.group(1)), float(orient_match.group(2)), float(orient_match.group(3))])
    
    # Buscar mensajes PID (cR, cP, cY)
    pid_match = pid_pattern.search(msg)
    if pid_match:
        timestamps_pid.append(ts)
        pid_values.append([float(pid_match.group(1)), float(pid_match.group(2)), float(pid_match.group(3))])

# Guardar a CSV separado para MATLAB

# PWM
if timestamps_pwm:
    df_pwm = pd.DataFrame(pwm_values, columns=['PWM1','PWM2','PWM3','PWM4'])
    df_pwm['timestamp'] = timestamps_pwm
    df_pwm.to_csv('PWM.csv', index=False)
    print(f"PWM.csv guardado con {len(pwm_values)} registros")
else:
    print("No se encontraron datos PWM")

# Orientación
if timestamps_orient:
    df_orient = pd.DataFrame(orient_values, columns=['roll','pitch','yaw'])
    df_orient['timestamp'] = timestamps_orient
    df_orient.to_csv('Orientacion.csv', index=False)
    print(f"Orientacion.csv guardado con {len(orient_values)} registros")
else:
    print("No se encontraron datos de Orientación")

# PID (cR, cP, cY)
if timestamps_pid:
    df_pid = pd.DataFrame(pid_values, columns=['cR','cP','cY'])
    df_pid['timestamp'] = timestamps_pid
    df_pid.to_csv('PID_controls.csv', index=False)
    print(f"PID_controls.csv guardado con {len(pid_values)} registros")
else:
    print("No se encontraron datos PID")

print("\nResumen:")
print(f"- Mensajes PWM: {len(pwm_values)}")
print(f"- Mensajes Orientación: {len(orient_values)}")
print(f"- Mensajes PID: {len(pid_values)}")