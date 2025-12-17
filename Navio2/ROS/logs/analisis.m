close all; clc, clear
% Cargar los CSV
PWM = readtable('PWM30-09.csv');
Orientacion = readtable('Orientacion30-09.csv');

% Convertir timestamp de segundos desde epoch a datetime
PWM_time = datetime(PWM.timestamp,'ConvertFrom','posixtime','Format','HH:mm:ss');
Orient_time = datetime(Orientacion.timestamp,'ConvertFrom','posixtime','Format','HH:mm:ss');

% Graficar PWM
figure;
subplot(2,2,1)
plot(PWM_time, PWM.PWM1, 'r'); title('PWM 1'); xlabel('Tiempo (HH:MM:SS)'); grid on;
subplot(2,2,2)
plot(PWM_time, PWM.PWM2, 'g'); title('PWM 2'); xlabel('Tiempo (HH:MM:SS)'); grid on;
subplot(2,2,3)
plot(PWM_time, PWM.PWM3, 'b'); title('PWM 3'); xlabel('Tiempo (HH:MM:SS)'); grid on;
subplot(2,2,4)
plot(PWM_time, PWM.PWM4, 'k'); title('PWM 4'); xlabel('Tiempo (HH:MM:SS)'); grid on;

% Graficar Orientación
figure;
plot(Orient_time, Orientacion.roll, 'r'); hold on
plot(Orient_time, Orientacion.pitch, 'g');
plot(Orient_time, Orientacion.yaw, 'b');
xlabel('Tiempo (HH:MM:SS)'); ylabel('Orientación'); title('Orientación vs Tiempo');
legend('Roll','Pitch','Yaw');
grid on;