# Envia mensajes mavlink para controlar el dron desde el simulador
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from pymavlink import mavutil
import time
import math

class control(Node):
    def __init__(self):
        super().__init__('mavlink')
        self.subsControl = self.create_subscription(
            Float32MultiArray,
            'dron_mov',
            self.controlCallback,
            10
        )
        self.get_logger().info("Nodo de mensajes mavlink iniciado")

        self.mavutil = mavutil
        try:
            # self.dron = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
            # self.dron = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
            self.dron = mavutil.mavlink_connection('udpin:localhost:14550')
        except Exception as e:
            self.get_logger().fatal(f"Error connecting to the vehicle: {e}")
            exit(1)
        self.dron.wait_heartbeat()

        self.dron.mav.set_mode_send(
            self.dron.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            4 # 4 = GUIDED
        )
        # armar
        self.dron.mav.command_long_send(
            self.dron.target_system,
            self.dron.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1,0,0,0,0,0,0
        )
        # checar armado
        msg = self.dron.recv_match(type='COMMAND_ACK', blocking=True)
        if msg.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
            self.get_logger().warn("fallo en armar")
            exit(1)
        self.get_logger().info("Armado")
        time.sleep(1)

        # auto despegue a 1 m
        self.dron.mav.command_long_send(
            self.dron.target_system,
            self.dron.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0,0,0,0,0,0,1
        )
        # checar cmd despegue
        msg = self.dron.recv_match(type='COMMAND_ACK', blocking=True)
        if msg.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
            self.get_logger().warn("fallo en despegue")
            exit(1)
        
    def controlCallback(self, msg):
        self.get_logger().info(str(msg.data))
        # Asegura que los datos sean float
        x = float(msg.data[0])
        y = float(msg.data[1])
        z = float(msg.data[2])
        yaw = float(msg.data[3])
        self.dron.mav.set_position_target_local_ned_send(
            0,
            self.dron.target_system,
            self.dron.target_component,
            self.mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            2503, # solo posicion
            0,0,0,
            x, y, z,
            0,0,0,
            math.radians(yaw), 0 # primer argumento controla dirección
        )
    
    def termina(self):
        self.dron.mav.command_long_send(
            self.dron.target_system,
            self.dron.target_component,
            self.mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
            0,
            0,0,0,0,0,0,0
        )
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    subsControl = control()
    try:
        rclpy.spin(subsControl)
    except KeyboardInterrupt:
        pass
    finally:
        subsControl.termina()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
