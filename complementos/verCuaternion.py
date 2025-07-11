import serial
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
    def __init__(self, port='/dev/ttyUSB0', baudrate=250000):
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.latest_quat = np.array([1., 0., 0., 0.])
        self.quaternion_buffer = deque(maxlen=200)
        self.freq_buffer = deque(maxlen=10)
        self.last_time = time.time()
        
        # Configuración de la figura
        self.fig = plt.figure(figsize=(14, 10))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.setup_plot()
        
        # Elementos de visualización
        self.setup_visual_elements()
        
    def setup_plot(self):
        """Configura los parámetros básicos del gráfico 3D"""
        self.ax.set_xlim(-1.5, 1.5)
        self.ax.set_ylim(-1.5, 1.5)
        self.ax.set_zlim(-1.5, 1.5)
        self.ax.set_title('Visualización de Orientación en Tiempo Real', fontsize=14)
        self.ax.set_xlabel('Eje X')
        self.ax.set_ylabel('Eje Y')
        self.ax.set_zlabel('Eje Z')
        self.ax.grid(True)
        
    def setup_visual_elements(self):
        """Crea y configura los elementos visuales"""
        # Ejes de referencia (fijos)
        self.ref_lines = [
            self.ax.plot([0, 1], [0, 0], [0, 0], 'r-', linewidth=2, alpha=0.3)[0],
            self.ax.plot([0, 0], [0, 1], [0, 0], 'g-', linewidth=2, alpha=0.3)[0],
            self.ax.plot([0, 0], [0, 0], [0, 1], 'b-', linewidth=2, alpha=0.3)[0]
        ]
        
        # Ejes rotados
        self.rot_lines = [
            self.ax.plot([], [], [], 'r-', linewidth=3)[0],
            self.ax.plot([], [], [], 'g-', linewidth=3)[0],
            self.ax.plot([], [], [], 'b-', linewidth=3)[0]
        ]
        
        # Trayectoria
        self.trajectory_line, = self.ax.plot([], [], [], 'y-', alpha=0.6, linewidth=1)
        
        # Texto informativo
        self.quat_text = self.ax.text2D(0.02, 0.95, "", transform=self.ax.transAxes, 
                                       fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        self.freq_text = self.ax.text2D(0.02, 0.90, "", transform=self.ax.transAxes,
                                      fontsize=9, bbox=dict(facecolor='white', alpha=0.7))
        self.sys_text = self.ax.text2D(0.70, 0.95, "Sistema de Referencia", 
                                      transform=self.ax.transAxes, fontsize=9, color='gray')
        
    def start_serial_thread(self):
        """Inicia el hilo para lectura del puerto serial"""
        self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.serial_thread.start()
        
    def read_serial_data(self):
        """Lee datos del puerto serial en un hilo separado"""
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                print(f"Conexión establecida a {self.port} a {self.baudrate} bps")
                
                while self.running:
                    try:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if line and line.count(',') >= 3:
                            parts = [float(x) for x in line.split(',')[:4]]
                            if len(parts) == 4:
                                q = np.array(parts)
                                norm = np.linalg.norm(q)
                                if norm > 0:
                                    q /= norm  # Normalización
                                    self.latest_quat = q
                                    self.quaternion_buffer.append(q)
                                    
                                    # Calcular frecuencia de actualización
                                    current_time = time.time()
                                    self.freq_buffer.append(1 / (current_time - self.last_time))
                                    self.last_time = current_time
                    except (ValueError, IndexError) as e:
                        print(f"Error procesando datos: {e}")
                        continue
                        
        except serial.SerialException as e:
            print(f"Error en el puerto serial: {e}")
            self.running = False
            sys.exit(1)
            
    def update_plot(self, frame):
        """Actualiza la visualización 3D"""
        try:
            q = self.latest_quat
            
            # Actualizar información textual
            self.quat_text.set_text(
                f"Cuaternión:\n"
                f"w = {q[0]:.4f}\n"
                f"x = {q[1]:.4f}\n"
                f"y = {q[2]:.4f}\n"
                f"z = {q[3]:.4f}"
            )
            
            if self.freq_buffer:
                avg_freq = sum(self.freq_buffer) / len(self.freq_buffer)
                self.freq_text.set_text(f"Frecuencia: {avg_freq:.1f} Hz")
            
            # Calcular matriz de rotación
            rot_mat = quat2mat(q)
            
            # Actualizar ejes rotados
            coords = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
            rotated_coords = np.dot(coords[1:], rot_mat.T)
            
            for i, line in enumerate(self.rot_lines):
                x = [coords[0, 0], rotated_coords[i, 0]]
                y = [coords[0, 1], rotated_coords[i, 1]]
                z = [coords[0, 2], rotated_coords[i, 2]]
                line.set_data(x, y)
                line.set_3d_properties(z)
            
            # Actualizar trayectoria (usando la dirección X)
            if len(self.quaternion_buffer) > 1:
                traj_coords = np.array([quat2mat(q)[:,0] for q in self.quaternion_buffer])
                self.trajectory_line.set_data(traj_coords[:,0], traj_coords[:,1])
                self.trajectory_line.set_3d_properties(traj_coords[:,2])
                
        except Exception as e:
            print(f"Error en actualización: {e}")
        
        return self.rot_lines + [self.quat_text, self.freq_text, self.trajectory_line]
    
    def run(self):
        """Ejecuta la visualización"""
        self.start_serial_thread()
        
        # Configurar cierre limpio
        def on_close(event):
            self.running = False
            print("\nVisualización cerrada correctamente")
            
        self.fig.canvas.mpl_connect('close_event', on_close)
        
        # Iniciar animación
        ani = FuncAnimation(
            self.fig, 
            self.update_plot, 
            frames=None,
            init_func=lambda: self.rot_lines + [self.quat_text, self.freq_text, self.trajectory_line],
            blit=True, 
            interval=20, 
            cache_frame_data=False
        )
        
        plt.tight_layout()
        plt.show()
        self.running = False

if __name__ == "__main__":
    # Configuración (ajustar según necesidad)
    visualizer = QuaternionVisualizer(
        port='/dev/ttyUSB1',  # Cambiar por tu puerto (COMx en Windows)
        baudrate=250000
    )
    visualizer.run()