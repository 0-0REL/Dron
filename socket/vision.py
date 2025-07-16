import cv2
import socket

class Vision:
    def __init__(self):
        self.source = cv2.VideoCapture(0)
        self.win_name = "Camera Preview"
        cv2.namedWindow(self.win_name, cv2.WINDOW_NORMAL)

        prototxt_path = '/home/rodrigo/Documentos/apm_ws/src/socket/deploy.prototxt'
        caffemodel_path = '/home/rodrigo/Documentos/apm_ws/src/socket/res10_300x300_ssd_iter_140000_fp16.caffemodel'

        self.net = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)
        self.in_width = 300
        self.in_height = 300
        self.mean = [104, 117, 123]
        self.conf_threshold = 0.7

        self.x = 0.0  # area
        self.y = 0.0  # x centro relativo
        self.z = 0.0  # y centro relativo

        # Socket UDP para enviar datos
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.CTRL_ADDR = ('localhost', 5005)  # Cambia IP/puerto según tu receptor

    def enviar_info(self, x, y, z):
        msg = f"{x},{y},{z}"
        self.sock.sendto(msg.encode(), self.CTRL_ADDR)

    def procesar_frame(self):
        has_frame, frame = self.source.read()
        if not has_frame:
            print("No se pudo leer frame de la cámara.")
            return

        frame = cv2.flip(frame, 1)
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]

        blob = cv2.dnn.blobFromImage(frame, 1.0, (self.in_width, self.in_height), self.mean, swapRB=False, crop=False)
        self.net.setInput(blob)
        detections = self.net.forward()

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.conf_threshold:
                x_top_left = int(detections[0, 0, i, 3] * frame_width)
                y_top_left = int(detections[0, 0, i, 4] * frame_height)
                x_bottom_right = int(detections[0, 0, i, 5] * frame_width)
                y_bottom_right = int(detections[0, 0, i, 6] * frame_height)

                cv2.rectangle(frame, (x_top_left, y_top_left), (x_bottom_right, y_bottom_right), (0, 255, 0))
                area = (x_bottom_right - x_top_left) * (y_bottom_right - y_top_left)
                label = "area: %.4f" % area
                label_size, base_line = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                cv2.rectangle(
                    frame,
                    (x_top_left, y_top_left - label_size[1]),
                    (x_top_left + label_size[0], y_top_left + base_line),
                    (255, 255, 255),
                    cv2.FILLED,
                )
                cv2.putText(frame, label, (x_top_left, y_top_left), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

                # Centro del bounding box relativo al centro de la imagen
                x_center = (x_top_left + x_bottom_right) // 2
                y_center = (y_top_left + y_bottom_right) // 2
                self.x = area
                self.y = x_center - (frame_width // 2)
                self.z = y_center - (frame_height // 2)

                # Solo envía la primera detección válida
                break

        t, _ = self.net.getPerfProfile()
        label = "Inference time: %.2f ms" % (t * 1000.0 / cv2.getTickFrequency())
        cv2.putText(frame, label, (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
        cv2.imshow(self.win_name, frame)
        cv2.waitKey(1)  # Necesario para refrescar la ventana
        self.enviar_info(self.x, self.y, self.z)

    def destroy(self):
        self.source.release()
        cv2.destroyAllWindows()

def main():
    vis = Vision()
    try:
        while True:
            vis.procesar_frame()
    except KeyboardInterrupt:
        pass
    vis.destroy()

if __name__ == '__main__':
    main()