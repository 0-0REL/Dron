import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from ament_index_python.packages import get_package_share_directory
import cv2

class vision(Node):
    def __init__(self):
        super().__init__('face_detection')
        self.publisher = self.create_publisher(Vector3, 'face_pos', 10)
        self.get_logger().info("Nodo de visión iniciado")

        self.cv2 = cv2
        self.source = cv2.VideoCapture(0)
        self.win_name = "Camera Preview"
        cv2.namedWindow(self.win_name, cv2.WINDOW_NORMAL)

        prototxt_path = 'src/vision/vision/deploy.prototxt'
        caffemodel_path = 'src/vision/vision/res10_300x300_ssd_iter_140000_fp16.caffemodel'

        self.net = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)
        self.in_width = 300
        self.in_height = 300
        self.mean = [104, 117, 123]
        self.conf_threshold = 0.7

        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        # Timer para procesar frames cada 50 ms (~20 Hz)
        self.timer = self.create_timer(1/20, self.procesar_frame)

    def publicar_info(self, x, y, z):
        msg = Vector3()
        msg.x = float(x)
        msg.y = float(y)
        msg.z = float(z)
        self.publisher.publish(msg)
        self.get_logger().info(f"face in: x={x}, y={y}, z={z}")

    def procesar_frame(self):
        has_frame, frame = self.source.read()
        if not has_frame:
            self.get_logger().warn("No se pudo leer frame de la cámara.")
            return

        frame = self.cv2.flip(frame, 1)
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]

        blob = self.cv2.dnn.blobFromImage(frame, 1.0, (self.in_width, self.in_height), self.mean, swapRB=False, crop=False)
        self.net.setInput(blob)
        detections = self.net.forward()

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.conf_threshold:
                x_top_left = int(detections[0, 0, 0, 3] * frame_width)
                y_top_left = int(detections[0, 0, 0, 4] * frame_height)
                x_bottom_right = int(detections[0, 0, 0, 5] * frame_width)
                y_bottom_right = int(detections[0, 0, 0, 6] * frame_height)

                self.cv2.rectangle(frame, (x_top_left, y_top_left), (x_bottom_right, y_bottom_right), (0, 255, 0))
                #label = "Confidence: %.4f" % confidence
                area = ((x_bottom_right-x_top_left) * (y_bottom_right-y_top_left))
                label = "area: %.4f" % area
                label_size, base_line = self.cv2.getTextSize(label, self.cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                self.cv2.rectangle(
                    frame,
                    (x_top_left, y_top_left - label_size[1]),
                    (x_top_left + label_size[0], y_top_left + base_line),
                    (255, 255, 255),
                    self.cv2.FILLED,
                )
                self.cv2.putText(frame, label, (x_top_left, y_top_left), self.cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

                self.x = area
                self.y = (x_top_left + x_bottom_right)//2 - (frame_width // 2)
                self.z = (y_top_left + y_bottom_right)//2 - (frame_height // 2)

        t, _ = self.net.getPerfProfile()
        label = "Inference time: %.2f ms" % (t * 1000.0 / self.cv2.getTickFrequency())
        self.cv2.putText(frame, label, (0, 15), self.cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
        self.cv2.imshow(self.win_name, frame)
        self.cv2.waitKey(1)  # Necesario para refrescar la ventana
        self.publicar_info(self.x,self.y,self.z)

    def destroy(self):
        self.source.release()
        self.cv2.destroyAllWindows()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    vis = vision()
    try:
        rclpy.spin(vis)
    except KeyboardInterrupt:
        pass
    vis.destroy()
    rclpy.shutdown()

if __name__ == '__main__':
    main()