clc;
clear;
close all;
format short

tic
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Parámetros de simulación: 
    h = 0.01;  % Step size for the ODE solver
    ts = 0:h:5;  % 5s
    opciones=odeset('RelTol' ,1e-06, 'AbsTol',1e-06,'InitialStep' ,h,'MaxStep',h);
    
%-------------------------------------------------------------------------%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Solución del sistema:
% condiciones_iniciales=[0; 0; 0; 0; 0; 0;0;0;0; 0.01; 0.01; 0.01; 0; 0; 0;0;0;0;0;0;0;0;0;0;0;0];
% [t,x]=ode45('DinamicaDronCompleto',ts,condiciones_iniciales,opciones);
x0 = [0 0 0 0 0 0 0.2 0.1 0.05 0.01 0 0]';
[t,x] = ode45('Dinamica12', ts, x0, opciones);

% figure
% plot(t, x(:,1),t,x(:,2), t,x(:,3))
% title('Posicion \xi')
% legend('X', 'Y', 'Z')
% xlabel('Tiempo (s)')
% ylabel('Posicion (m)')
% 
figure
plot(t, x(:,7),t,x(:,8), t,x(:,9))
title('Orientacion \eta')
legend('\phi', '\theta', '\psi')
xlabel('Tiempo (s)')
ylabel('Orientacion (rad)')

% figure
% tcl = tiledlayout(2, 2, 'TileSpacing','tight'); 
% nexttile; 
% plot(t, x(:,19));
% title('\Omega_1');
% 
% nexttile; 
% plot(t, x(:,20)); 
% title('\Omega_2');
% 
% nexttile; 
% plot(t, x(:,21));
% title('\Omega_3');
% 
% nexttile; 
% plot(t, x(:,22));
% title('\Omega_4');
% 
% title(tcl,'Velocidad Motores')
% xlabel(tcl,'Tiempo (s)')
% ylabel(tcl,'Revoluciones (rad/s)')

%-------------------------------------------------------------------------%
toc