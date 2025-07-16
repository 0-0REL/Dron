import socket
from pymavlink import mavutil
import time

class SimpleMav:
    def __init__(self, mode=4):  # 4 = GUIDED mode
        try:
            self.master = mavutil.mavlink_connection('udpin:localhost:14550')
        except Exception as e:
            print("Error connecting to the vehicle: ", e)
            exit(1)
        self.master.wait_heartbeat()
        self.master.mav.set_mode_send(
            self.master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode
        )
    def armar(self, armar=1):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            armar,0,0,0,0,0,0
        )
    def despegue(self, altitud=1):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0,0,0,0,0,0,altitud
        )
    def aterrizar(self):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND,
            0,
            0,0,0,0,0,0,0
        )
    def rc_control(self, Roll=65535, Pitch=65535, Throttle=65535, Yaw=65535):
        def clamp(val):
            return max(0, min(65535, int(val)))
        self.master.mav.rc_channels_override_send(
            self.master.target_system,
            self.master.target_component,
            clamp(Roll), clamp(Pitch), clamp(Throttle), clamp(Yaw),
            65535, 65535, 65535, 65535
        )
    def intervalo_msg(self, msg_id, f_Hz):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
            getattr(mavutil.mavlink, f'MAVLINK_MSG_ID_{msg_id}'),
            1e6 / f_Hz,
            0, 0, 0, 0,
            0,
        )
    def recibir_msg(self, msg_type):
        return self.master.recv_match(type=msg_type, blocking=True)
    
    def fin(self):
        self.master.close()

def main():
    # Socket UDP para recibir comandos de control
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 5006))  # Puerto para recibir de control

    # Socket UDP para publicar altitud
    pub_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    PUB_ADDR = ('localhost', 5007)  # Cambia IP/puerto según tu receptor

    uav = SimpleMav(4)  # GUIDED mode
    uav.intervalo_msg('VFR_HUD', 30)
    uav.intervalo_msg('ATTITUDE', 30)
    uav.armar(1)
    time.sleep(3)
    alt_ini = uav.recibir_msg('VFR_HUD').alt

    print("Esperando comandos por UDP en puerto 5006...")
    try:
        while True:
            # Recibe comando por socket: "Pitch,Yaw,Throttle"
            data, _ = sock.recvfrom(1024)
            try:
                pitch, yaw, throttle = map(float, data.decode().split(','))
            except Exception as e:
                print("Error en datos recibidos:", e)
                continue
            uav.rc_control(Pitch=1500+pitch, Yaw=1500+yaw, Throttle=throttle)

            # Publica altitud actual por socket
            alt_actual = uav.recibir_msg('VFR_HUD').alt
            alt_diff = alt_actual - alt_ini
            pub_sock.sendto(f"{alt_diff:.2f}".encode(), PUB_ADDR)
            print(f"Publicando altitud: {alt_diff:.2f} m")
    except KeyboardInterrupt:
        print("Cerrando conexión MAVLink y sockets.")
    finally:
        uav.fin()
        sock.close()
        pub_sock.close()

if __name__ == '__main__':
    main()