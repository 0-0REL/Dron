import cv2
import os
import time

# Configuración de la cámara
source = cv2.VideoCapture(0)
win_name = "Camera Preview"
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)

# Cargar modelo de detección facial
net = cv2.dnn.readNetFromCaffe("complementos/modelos/deploy.prototxt", 
                             "complementos/modelos/res10_300x300_ssd_iter_140000_fp16.caffemodel")

# Parámetros del modelo
in_width = 300
in_height = 300
mean = [104, 117, 123]
conf_threshold = 0.7

# Directorio para guardar rostros
output_dir = "tensor/dataset/ignacio"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

frame_count = 51
last_face = None  # Para guardar el último rostro detectado

while True:
    has_frame, frame = source.read()
    if not has_frame:
        break
    
    frame = cv2.flip(frame, 1)
    frame_height = frame.shape[0]
    frame_width = frame.shape[1]

    # Preprocesamiento para la red neuronal
    blob = cv2.dnn.blobFromImage(frame, 1.0, (in_width, in_height), mean, swapRB=False, crop=False)
    net.setInput(blob)
    detections = net.forward()

    #for i in range(detections.shape[2]):
    confidence = detections[0, 0, 0, 2]
    if confidence > conf_threshold:
        # Coordenadas del rostro detectado
        x_top_left = int(detections[0, 0, 0, 3] * frame_width)
        y_top_left = int(detections[0, 0, 0, 4] * frame_height)
        x_bottom_right = int(detections[0, 0, 0, 5] * frame_width)
        y_bottom_right = int(detections[0, 0, 0, 6] * frame_height)
        
        # Asegurar que las coordenadas estén dentro del frame
        x_top_left = max(0, x_top_left)
        y_top_left = max(0, y_top_left)
        x_bottom_right = min(frame_width, x_bottom_right)
        y_bottom_right = min(frame_height, y_bottom_right)    

        # Recortar y redimensionar el rostro
        face = frame[y_top_left:y_bottom_right, x_top_left:x_bottom_right]
        if face.size > 0:  # Verificar que el recorte no esté vacío
            face_resized = cv2.resize(face, (250, 250))
            last_face = face_resized  # Guarda el último rostro detectado

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC para salir
        break
    elif key == ord('s'):
        if last_face is not None:
            filename = f"{output_dir}/rostro_{frame_count}.jpg"
            cv2.imwrite(filename, last_face)
            print(f"Rostro guardado: {filename}")
            frame_count += 1
    # Dibujar rectángulo alrededor del rostro
    cv2.rectangle(frame, (x_top_left, y_top_left), (x_bottom_right, y_bottom_right), (0, 255, 0), 2)
            
    # Mostrar información de tiempo
    t, _ = net.getPerfProfile()
    label = "Inference time: %.2f ms" % (t * 1000.0 / cv2.getTickFrequency())
    cv2.putText(frame, label, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
    
    # Contador de rostros guardados
    cv2.putText(frame, f"Rostros guardados: {frame_count}", (10, 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255))
    
    cv2.imshow(win_name, frame) 

source.release()
cv2.destroyAllWindows()