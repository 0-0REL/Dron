# Envia mensajes mavlink para controlar el dron desde el simulador
#!/home/rodrigo/Documentos/Prog/Python/entV/bin/python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import Float32MultiArray
from simple_pid import PID

class control(Node):
    def __init__(self):
        super().__init__('nodo_control')
        self.pubControl = self.create_publisher(Float32MultiArray, 'dron_mov', 10)
        self.subsVision = self.create_subscription(
            Vector3,
            'vision_data',
            self.controlCallback,
            10
        )
        self.get_logger().info("Nodo de control iniciado")
        self.thro_pid = PID(0.3, 0.001, 0.01, setpoint=15, sample_time=0.5, output_limits=(-3, 3))
        self.pitch_pid = PID(0.3, 0.001, 0.01, setpoint=15, sample_time=0.5, output_limits=(-3, 3))
        self.yaw_pid = PID(0.3, 0.001, 0.01, setpoint=15, sample_time=0.5, output_limits=(-3, 3))

    def publicar_control(self, x, y, z, yaw):
        msg = Float32MultiArray()
        msg.data = [float(x), float(y), float(z), float(yaw)]
        self.pubControl.publish(msg)
        self.get_logger().info(f"Publicando datos de control: x={x}, y={y}, z={z}, yaw={yaw}")

    def controlCallback(self, msg):
        self.get_logger().info(str(msg))
        distancia = self.pitch_pid(msg.x)
        giro = self.yaw_pid(msg.y)
        altura = self.thro_pid(msg.z)
        yaw = 0.0  # Puedes calcular el yaw deseado aquí si aplica
        self.publicar_control(distancia, giro, altura, yaw)
    
    def finControl(self):
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    subsControl = control()
    try:
        rclpy.spin(subsControl)
    except KeyboardInterrupt:
        pass
    subsControl.finControl()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
