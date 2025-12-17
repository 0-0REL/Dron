% 13/11/2025
% Sintonizacion de controladores PD y PID mediante modelo lineal en discreto
close all; clc, clear
% Datos
m = 1.6;                    % Masa del dron
L = 0.268554;               % Distancia del centrol de gravedad a helices
kF = 0.7*9.81;              % Coeficiente de empuje N por milisegndos
kM = 0.1;                   % Coeficiente de arrastre N por milisegundos
km = log(1-0.9933)/-0.1;    % Coeficiente de reatraso de en la aceleracion de los motores
I = diag([0.021915027 0.022124548 0.042349865]);    % Matriz de inercia
Ts = 1/510;                 % Periodo de muestreo

motor = tf(km,[1 km]);      % funcion de trasferencia de los motores
%% Control de altura
alt = tf (1, [m 0 0]);
sys = series(motor, alt);
%dSys = c2d(cSys,Ts,'zoh');
controlSystemDesigner(sys)
%% Control de roll
aX = tf(1,[I(1,1) 0 0]);
sys = series(motor,aX);
% dSys = c2d(cSys,Ts,'zoh');
controlSystemDesigner(sys)
%% Control de pitch
aY = tf(1,[I(2,2) 0 0]);
sys = series(motor,aY);
% dSys = c2d(cSys,Ts,'zoh');
controlSystemDesigner(sys)
%% Control de yaw
aZ = tf(1,[I(3,3) 0 0]);
sys = series(motor,aZ);
% dSys = c2d(cSys,Ts,'zoh');
controlSystemDesigner(sys)