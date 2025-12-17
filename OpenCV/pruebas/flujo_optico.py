# flujo optico
# del tutorial de opencv

import cv2
import numpy as np

def dense_optical_flow(video_path, to_gray=False):
    # Read the video and first frame
    cap = cv2.VideoCapture(video_path)
    ret, old_frame = cap.read()
 
    # create HSV & make Value a constant
    hsv = np.zeros_like(old_frame)
    hsv[..., 1] = 255
 
    # Preprocessing for exact method
    if to_gray:
        old_frame = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    while True:
        # Read the next frame
        ret, new_frame = cap.read()
        frame_copy = new_frame
        if not ret:
            break
    
        # Preprocessing for exact method
        if to_gray:
            new_frame = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
        method = cv2.optflow.calcOpticalFlowSparseToDense

        # Parámetros para el método (puedes ajustar según tu necesidad)
        params = ()
    
        # Calculate Optical Flow
        flow = method(old_frame, new_frame, None, *params)
    
        # Encoding: convert the algorithm's output into Polar coordinates
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        # Use Hue and Value to encode the Optical Flow
        hsv[..., 0] = ang * 180 / np.pi / 2
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    
        # Convert HSV image into BGR for demo
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        cv2.imshow("frame", frame_copy)
        cv2.imshow("optical flow", bgr)
        k = cv2.waitKey(25) & 0xFF
        if k == 27:
            break
    
        # Update the previous frame
        old_frame = new_frame

    cap.release()
    cv2.destroyAllWindows()

def lucas_kanade_method(video_path):
    # Read the video 
    cap = cv2.VideoCapture(video_path)
 
    # Parameters for ShiTomasi corner detection
    feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
 
    # Parameters for Lucas Kanade optical flow
    lk_params = dict(
        winSize=(15, 15),
        maxLevel=2,
        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
    )
 
    # Create random colors
    color = np.random.randint(0, 255, (100, 3))
 
    # Take first frame and find corners in it
    ret, old_frame = cap.read()
    if not ret:
        print("No se pudo leer el video.")
        return
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
 
    # Create a mask image for drawing purposes
    mask = np.zeros_like(old_frame)
    while True:
        # Read new frame
        ret, frame = cap.read()
        if not ret:
            break
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        # Calculate Optical Flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(
            old_gray, frame_gray, p0, None, **lk_params
        )
        # Select good points
        if p1 is None or st is None:
            break
        good_new = p1[st == 1]
        good_old = p0[st == 1]
    
        # Draw the tracks
        for i, (new, old) in enumerate(zip(good_new, good_old)):
            a, b = new.ravel()
            c, d = old.ravel()
            mask = cv2.line(mask, (int(a), int(b)), (int(c), int(d)), color[i % 100].tolist(), 2)
            frame = cv2.circle(frame, (int(a), int(b)), 5, color[i % 100].tolist(), -1)
    
        # Display the demo
        img = cv2.add(frame, mask)
        cv2.imshow("Lucas-Kanade Optical Flow", img)
        k = cv2.waitKey(25) & 0xFF
        if k == 27:
            break
    
        # Update the previous frame and previous points
        old_gray = frame_gray.copy()
        p0 = good_new.reshape(-1, 1, 2)
    cap.release()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    # Puedes cambiar el nombre del video y si quieres convertir a escala de grises
    #dense_optical_flow(0, to_gray=True)
    lucas_kanade_method(0)
# dense_optical_flow.py
# Ejemplo de uso:
# dense_optical_flow("video.mp4", to_gray=True)