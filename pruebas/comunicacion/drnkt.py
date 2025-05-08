# Prueba con dronkit
from dronekit import connect

# conectar a dron
dron = connect('127.0.0.1:14550', wait_ready=True)
#dron = connect('dev/ttyACM0', wait_ready=True)

# probando resepcion de mensajes
print('version:', dron.version)
print('bateria:', dron.battery)
print('capacidades:',dron.capabilities.ftp)
print('EKF?:',dron.ekf_ok)
print('se puede armar?:',dron.is_armable)
print('estado de sistema',dron.system_status.state)
print('modo:',dron.mode.name)
print('armado?:',dron.armed)

# trata de armar
#dron.mode = VehicleMode("GUIDED")
dron.arm = True

dron.simple_takeoff(1)
