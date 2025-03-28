import cv2
import mediapipe

def marca(infDetc,fram):
    '''Crea rectangulo que encierra el rostro'''
    caja = infDetc.location_data.relative_bounding_box
    x = int(caja.xmin * fram.shape[1])
    y = int(caja.ymin * fram.shape[0])
    ancho = int(caja.width * fram.shape[1])
    alto = int(caja.height * fram.shape[0])
    cv2.rectangle(fram,(x,y), (x+ancho,y+alto),(0,255,0),2)
# Camara
cam = cv2.VideoCapture(0)

with mediapipe.solutions.face_detection.FaceDetection(
    min_detection_confidence = 0.5) as Detec_Rost:
    while True:
        fok,frmBGR = cam.read()
        if fok is False:
            print('No camara')
            break
        frmRGB = cv2.cvtColor(frmBGR,cv2.COLOR_BGR2RGB)
        rslt = Detec_Rost.process(frmRGB)
        # Detiene camara si no hay nadie
        if rslt.detections is None:
            continue
        for ndetec in rslt.detections:
            #mediapipe.solutions.drawing_utils.draw_detection(frmBGR,ndetec)
            marca(ndetec,frmBGR)
        cv2.imshow("Deteccion de rostro", cv2.flip(frmBGR,1))
        if cv2.waitKey(20) & 0xFF == ord("q"):
            break
# Liberar
cam.release()
cv2.destroyAllWindows()
