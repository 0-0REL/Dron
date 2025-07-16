import socket
from simple_pid import PID

class Control:
    def __init__(self):
        # Sockets UDP
        self.sock_vision = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_vision.bind(('localhost', 5005))  # Recibe de vision.py

        self.sock_mav = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_mav.bind(('localhost', 5007))     # Recibe altitud de mav_msgs.py

        self.sock_cmd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.MAV_ADDR = ('localhost', 5006)         # Envía comandos a mav_msgs.py

        # PIDs para control
        self.thro_pid = PID(100, 100, 50, output_limits=(1000, 2000))
        self.pitch_pid = PID(0.3, 0.001, 0.01, setpoint=28, output_limits=(-500, 500))
        self.yaw_pid = PID(0.3, 0.001, 0.01, output_limits=(-500, 500))
        self.yaw_pid.setpoint = 0
        self.thro_pid.setpoint = 1

        self.distancia = 0
        self.yaw = 0
        self.throttle = 0

    def run(self):
        import threading
        threading.Thread(target=self.listen_vision, daemon=True).start()
        threading.Thread(target=self.listen_mav, daemon=True).start()
        try:
            while True:
                # Envía comando cada 50 ms
                msg = f"{self.distancia},{self.yaw},{self.throttle}"
                self.sock_cmd.sendto(msg.encode(), self.MAV_ADDR)
                print(f"Enviado: distancia={self.distancia:.2f}, yaw={self.yaw:.2f}, throttle={self.throttle:.2f}")
                import time
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("Cerrando sockets.")
        finally:
            self.sock_vision.close()
            self.sock_mav.close()
            self.sock_cmd.close()

    def listen_vision(self):
        while True:
            data, _ = self.sock_vision.recvfrom(1024)
            try:
                x, y, z = map(float, data.decode().split(','))
            except Exception as e:
                print("Error en datos de visión:", e)
                continue
            self.distancia = self.pitch_pid(x/1000)
            self.yaw = self.yaw_pid(y)
            # self.thro_pid.setpoint = z  # Si quieres usar z como setpoint

    def listen_mav(self):
        while True:
            data, _ = self.sock_mav.recvfrom(1024)
            try:
                alt = float(data.decode())
            except Exception as e:
                print("Error en datos de altitud:", e)
                continue
            self.throttle = self.thro_pid(alt)

if __name__ == '__main__':
    ctrl = Control()
    ctrl.run()