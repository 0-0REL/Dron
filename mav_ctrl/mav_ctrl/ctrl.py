# ros
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import Float32

# no ros
from simple_pid import PID

class control(Node):
    def __init__(self):
        super().__init__('control')
        self.pubControl = self.create_publisher(Vector3, 'mv_dron', 10)
        self.subsVision = self.create_subscription(Vector3, 'face_pos', self.CamCallback, 10)
        self.subsMav = self.create_subscription(Float32, 'mav_msgs', self.mavCallback, 10)
        self.get_logger().info("Nodo de control iniciado")
        # PIDs para control
        self.thro_pid = PID(0.5, 0.01, 0, output_limits=(0, 1))
        self.pitch_pid = PID(0, 0, 0, setpoint=28, output_limits=(-0.5, 0.5))
        self.yaw_pid = PID(0.3, 0.001, 0.01, output_limits=(-0.5, 0.5))

        #self.VFD = 0
        #self.ATTIDUDE = 0
        self.yaw_pid.setpoint = 0
        self.thro_pid.setpoint = 1

        self.distancia = 0
        self.yaw = 0
        self.throttle = 0
        
        #self.timer = self.create_timer(1/20, self.control)

    def publicar_control(self, x, y, z=0):
        msg = Vector3()
        msg.x = float(x)*100
        msg.y = float(y)*100
        msg.z = float(z)*1000
        self.pubControl.publish(msg)
        self.get_logger().info(f"distancia={x:.2f}, yaw={y:.2f}, throttle={z:.2f}")

    def CamCallback(self, msg):
        self.distancia = self.pitch_pid(msg.x/1000)
        self.yaw = self.yaw_pid(msg.y)
        #self.thro_pid.setpoint = msg.z

    def mavCallback(self, msg):
        self.throttle = self.thro_pid(msg.data)
        self.control()

    def finControl(self):
        super().destroy_node()

    def control(self):
        self.publicar_control(self.distancia, self.yaw, self.throttle)


def main(args=None):
    rclpy.init(args=args)
    cont = control() 
    try:
        rclpy.spin(cont)
    except KeyboardInterrupt:
        pass
    cont.finControl()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
