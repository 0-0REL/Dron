# ros
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import Float32
#
from pymavlink import mavutil
import time

class mav_msg(Node):
    def __init__(self):
        super().__init__('mavlink')
        self.pubMav = self.create_publisher(Float32, 'mav_msgs', 10)
        self.subsCtrl = self.create_subscription(Vector3, 'mv_dron', self.mavCallback, 10)
        self.get_logger().info("Nodo de publicacion mavlink iniciado")

        self.uav = SimpleMav(0)  # 0 estabilizar, 1 acro
        self.uav.intervalo_msg('VFR_HUD', 30)  #
        self.uav.intervalo_msg('ATTITUDE', 30)

        self.uav.armar(1)
        time.sleep(3)

        self.alt_ini = self.uav.recibir_msg('VFR_HUD').alt

        self.timer = self.create_timer(0.05, self.mav_publish)

    def mavCallback(self, msg):
        self.uav.rc_control(Pitch=1500+msg.x, Yaw=1500+msg.y, Throttle=msg.z)
    
    def mav_publish(self):
        msg = Float32()
        msg.data = self.uav.recibir_msg('VFR_HUD').alt - self.alt_ini
        self.pubMav.publish(msg)
        self.get_logger().info(f"Publicando: {msg.data:.2f} m")

    def finMav(self):
        self.uav.fin()
        super().destroy_node()


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
        self.master.mav.rc_channels_override_send(
            self.master.target_system,
            self.master.target_component,
            int(Roll), int(Pitch), int(Throttle), int(Yaw), 65535, 65535, 65535, 65535
        )
    def intervalo_msg(self, msg_id, f_Hz):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
            getattr(mavutil.mavlink, f'MAVLINK_MSG_ID_{msg_id}'), # The MAVLink message ID
            1e6 / f_Hz, # The interval between two messages in microseconds. Set to -1 to disable and 0 to request default rate.
            0, 0, 0, 0, # Unused parameters
            0, # Target address of message stream (if message has target address fields). 0: Flight-stack default (recommended), 1: address of requestor, 2: broadcast.
        )
    def recibir_msg(self, msg_type):
        return self.master.recv_match(type=msg_type, blocking=True)
    
    def fin(self):
        self.master.close()

def main(args=None):
    rclpy.init(args=args)
    mavlink = mav_msg()
    try:
        rclpy.spin(mavlink)
    except KeyboardInterrupt:
        pass
    mavlink.finMav()
    rclpy.shutdown()