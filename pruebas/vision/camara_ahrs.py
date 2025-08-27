import cv2
import serial
import math
import time

class camera_ahrs:
    def __init__(self, idxCam=0):
           self.cam = cv2.VideoCapture(idxCam)

    def camara(self, escala=1, roll=0, pitch=0):
        ret, frm = self.cam.read()
        if not ret:
            return None
        frm = cv2.flip(frm, 1)
        frm = cv2.resize(frm, dsize=None, fx=escala, fy=escala)
        (h, w) = frm.shape[:2]
        centro = (w//2, h//2)
        Mrot = cv2.getRotationMatrix2D(centro, roll, 1.0)
        rot_img = cv2.warpAffine(frm, Mrot, (w, h))
        altCent = int(centro[1] * (1 + math.tan(math.radians(pitch))))
        if altCent > h:
            altCent = h
        elif altCent < 0:
            altCent = 0
        cv2.circle(rot_img, (centro[0], altCent), 5, (0,0,255), -1)
        return rot_img

class imu_serial:
    def __init__(self, puerto='/dev/ttyUSB0', bps=115200):
        self.ser = serial.Serial(puerto, bps, timeout=1)
        time.sleep(2)  # Esperar a que se establezca la conexión
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
    
    def inclinacion(self):
        try:
            if self.ser.in_waiting > 0:
                linea = self.ser.readline().decode('utf-8').strip()
                
                # El formato esperado: "roll, pitch, yaw"
                if linea and ',' in linea:
                    datos = linea.split(',')
                    if len(datos) == 3:
                        self.roll = float(datos[0])
                        self.pitch = float(datos[1])
                        self.yaw = float(datos[2])
                        
                return self.roll, self.pitch, self.yaw
                
        except (serial.SerialException, ValueError, UnicodeDecodeError) as e:
            print(f"Error en lectura serial: {e}")
            return self.roll, self.pitch, self.yaw  # Retorna últimos valores válidos
        
if __name__ == "__main__":
    try:
        vid = camera_ahrs()
        ahrs = imu_serial(bps=250000)
        while cv2.waitKey(1) != 27:
            r, p, _ = ahrs.inclinacion()
            frame = vid.camara(0.5, r, p)
            print(r,p)
            if frame is None:
                continue
            cv2.imshow("Estabilizacion AHRS", frame)

        print('Programa finalizado')
    except KeyboardInterrupt:
        print('Programa abortado')
    finally:
        cv2.destroyAllWindows()
        vid.cam.release()
        if ahrs.ser.is_open:
            ahrs.ser.close()
