# regresa mensajes del dron por telemetría a la GCS

import threading
import time
import socket
from pymavlink import mavutil

# conexiones, dron y GCS
try:
    radio = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
except Exception as e:
    print("Error sin conexion al vehiculo: ", e)
    exit(1)

#try:
#    gcs = mavutil.mavlink_connection('udpout:localhost:14550')
#except Exception as e:
#    print("Error a local host: ", e)
#    exit(1)

out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip = "127.0.0.1"
port = 14550

radio.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (radio.target_system, radio.target_component))

def gcs_mp():
    while True:
        msg_gcs = radio.recv_match(blocking=True)
        if msg_gcs is not None:
            msg_envio = msg_gcs.get_type()
            if msg_envio:
                out.sendto(msg_gcs.encode(), (ip, port))
        else:
            print('Perdio conexión con el dron')

mp_gcs = threading.Thread(target=gcs_mp, daemon=True)
mp_gcs.start()

print('Probando comunicación entre el dron y la GCS')
while True:
    time.sleep(1)
