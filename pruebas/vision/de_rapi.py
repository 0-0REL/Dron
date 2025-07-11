import cv2
import numpy as np
import subprocess
import time

UDP_PORT = 9000
RPI_IP = "192.168.68.58"  # Cambia por la IP real de tu Raspberry
WIDTH, HEIGHT = 1280, 720

ffmpeg_cmd = [
    "ffmpeg",
    "-protocol_whitelist", "file,udp,tcp",
    "-i", f"tcp://{RPI_IP}:{UDP_PORT}?timeout=5000000",
    "-fflags", "nobuffer",
    "-flags", "low_delay",
    "-f", "image2pipe",
    "-pix_fmt", "bgr24",
    "-vcodec", "rawvideo",
    "-"
]

def restart_ffmpeg():
    return subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE)

process = restart_ffmpeg()

while True:
    try:
        raw_frame = process.stdout.read(WIDTH * HEIGHT * 3)
        if not raw_frame:
            print("Reiniciando FFmpeg...")
            process.terminate()
            process = restart_ffmpeg()
            time.sleep(1)
            continue
            
        frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
        cv2.imshow("Stream", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        print(f"Error: {e}")
        process.terminate()
        break

process.terminate()
cv2.destroyAllWindows()