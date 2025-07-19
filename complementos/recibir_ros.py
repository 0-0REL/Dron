import socket
import struct
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from transforms3d.quaternions import quat2mat
from collections import deque
import threading
import time
import sys

class QuaternionVisualizer:
    def __init__(self, udp_ip='0.0.0.0', udp_port=7000):
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.running = True
        self.latest_quat = np.array([1., 0., 0., 0.])
        self.quaternion_buffer = deque(maxlen=200)
        self.freq_buffer = deque(maxlen=10)
        self.last_time = time.time()
        
        # Configuración de la figura
        self.fig = plt.figure(figsize=(14, 10))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.setup_plot()
        self.setup_visual_elements()
        
    def setup_plot(self):
        """Configura los parámetros básicos del gráfico 3D"""
        self.ax.set_xlim(-1.5, 1.5)
        self.ax.set_ylim(-1.5, 1.5)
        self.ax.set_zlim(-1.5, 1.5)
        self.ax.set_title('Visualización de Orientación', fontsize=14)
        self.ax.set_xlabel('Eje X')
        self.ax.set_ylabel('Eje Y')
        self.ax.set_zlabel('Eje Z')
        self.ax.grid(True)
        
    def setup_visual_elements(self):
        """Configura los elementos visuales (igual que antes)"""
        self.ref_lines = [
            self.ax.plot([0, 1], [0, 0], [0, 0], 'r-', linewidth=2, alpha=0.3)[0],
            self.ax.plot([0, 0], [0, 1], [0, 0], 'g-', linewidth=2, alpha=0.3)[0],
            self.ax.plot([0, 0], [0, 0], [0, 1], 'b-', linewidth=2, alpha=0.3)[0]
        ]
        self.rot_lines = [
            self.ax.plot([], [], [], 'r-', linewidth=3)[0],
            self.ax.plot([], [], [], 'g-', linewidth=3)[0],
            self.ax.plot([], [], [], 'b-', linewidth=3)[0]
        ]
        self.trajectory_line, = self.ax.plot([], [], [], 'y-', alpha=0.6, linewidth=1)
        self.quat_text = self.ax.text2D(0.02, 0.95, "", transform=self.ax.transAxes, 
                                      fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        self.freq_text = self.ax.text2D(0.02, 0.90, "", transform=self.ax.transAxes,
                                      fontsize=9, bbox=dict(facecolor='white', alpha=0.7))
        
    def start_udp_thread(self):
        """Inicia el hilo para recibir datos por UDP"""
        self.udp_thread = threading.Thread(target=self.read_udp_data, daemon=True)
        self.udp_thread.start()
        
    def read_udp_data(self):
        """Lee datos del socket UDP en un hilo separado"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.udp_ip, self.udp_port))
        print(f"Escuchando en UDP {self.udp_ip}:{self.udp_port}...")
        
        while self.running:
            try:
                data, _ = sock.recvfrom(16)  # 16 bytes = 4 floats
                if len(data) == 16:
                    w, x, y, z = struct.unpack('ffff', data)
                    q = np.array([w, x, y, z])
                    norm = np.linalg.norm(q)
                    if norm > 0:
                        q /= norm  # Normalizar el cuaternión
                        self.latest_quat = q
                        self.quaternion_buffer.append(q)
                        
                        # Calcular frecuencia
                        current_time = time.time()
                        self.freq_buffer.append(1 / (current_time - self.last_time))
                        self.last_time = current_time
            except Exception as e:
                print(f"Error en UDP: {e}")
                continue
                
    def update_plot(self, frame):
        """Actualiza la visualización 3D (igual que antes)"""
        q = self.latest_quat
        
        # Actualizar texto
        self.quat_text.set_text(
            f"Cuaternión:\nw={q[0]:.4f}\nx={q[1]:.4f}\ny={q[2]:.4f}\nz={q[3]:.4f}"
        )
        if self.freq_buffer:
            self.freq_text.set_text(f"Frecuencia: {sum(self.freq_buffer)/len(self.freq_buffer):.1f} Hz")
        
        # Actualizar ejes y trayectoria
        rot_mat = quat2mat(q)
        coords = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
        rotated_coords = np.dot(coords[1:], rot_mat.T)
        
        for i, line in enumerate(self.rot_lines):
            x = [coords[0, 0], rotated_coords[i, 0]]
            y = [coords[0, 1], rotated_coords[i, 1]]
            z = [coords[0, 2], rotated_coords[i, 2]]
            line.set_data(x, y)
            line.set_3d_properties(z)
        
        if len(self.quaternion_buffer) > 1:
            traj_coords = np.array([quat2mat(q)[:,0] for q in self.quaternion_buffer])
            self.trajectory_line.set_data(traj_coords[:,0], traj_coords[:,1])
            self.trajectory_line.set_3d_properties(traj_coords[:,2])
        
        return self.rot_lines + [self.quat_text, self.freq_text, self.trajectory_line]
    
    def run(self):
        """Ejecuta la visualización"""
        self.start_udp_thread()
        
        def on_close(event):
            self.running = False
            print("\nVisualización cerrada")
            
        self.fig.canvas.mpl_connect('close_event', on_close)
        
        ani = FuncAnimation(
            self.fig, 
            self.update_plot, 
            blit=True, 
            interval=20,
            cache_frame_data=False
        )
        
        plt.tight_layout()
        plt.show()
        self.running = False

if __name__ == "__main__":
    visualizer = QuaternionVisualizer(udp_ip='0.0.0.0', udp_port=7000)
    visualizer.run()