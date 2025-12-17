close all; clear, clc
Orientacion = readtable('Orientacion01-10.csv');
control = readtable('PID01-10.csv');

% Graficar Orientación
figure;
Orient_time = datetime(Orientacion.timestamp,'ConvertFrom','posixtime','Format','HH:mm:ss');
plot(Orient_time, Orientacion.roll, 'r'); hold on
plot(Orient_time, Orientacion.pitch, 'g');
plot(Orient_time, Orientacion.yaw, 'b');
xlabel('Tiempo (HH:MM:SS)'); ylabel('Orientación'); title('Orientación vs Tiempo');
legend('Roll','Pitch','Yaw');
grid on;
% graficar control
control_time = datetime(control.timestamp,'ConvertFrom','posixtime','Format','HH:mm:ss');
figure;
plot(control_time, control.cR, 'r'); hold on
plot(control_time, control.cP, 'g');
plot(control_time, control.cY, 'b'); 
legend('Roll','Pitch','Yaw');
grid on;
% graficar salida a motores
Mr = control.cR;
Mp = control.cP;
My = control.cY;
F = 15.6960;
L = 0.268554;
kF = 0.7*9.81;
kM = 0.2;
mot1 = 1000.0 + (-(kM*Mr - kM*Mp - F*L*kM + kF*L*My)/(4*kF*L*kM))*1000.0;
mot2 = 1000.0 + (-(kM*Mr + kM*Mp - F*L*kM - kF*L*My)/(4*kF*L*kM))*1000.0;
mot3 = 1000.0 + ((kM*Mr - kM*Mp + F*L*kM - kF*L*My)/(4*kF*L*kM))*1000.0;
mot4 = 1000.0 + ((kM*Mr + kM*Mp + F*L*kM + kF*L*My)/(4*kF*L*kM))*1000.0;
figure
subplot(2,2,1)
plot(control_time, mot1, 'r'); title('motor 1'); xlabel('Tiempo (HH:MM:SS)'); grid on;
subplot(2,2,2)
plot(control_time, mot2, 'g'); title('Motor 2'); xlabel('Tiempo (HH:MM:SS)'); grid on;
subplot(2,2,3)
plot(control_time, mot3, 'b'); title('Motor 3'); xlabel('Tiempo (HH:MM:SS)'); grid on;
subplot(2,2,4)
plot(control_time, mot4); title('Motor 4'); xlabel('Tiempo (HH:MM:SS)'); grid on;