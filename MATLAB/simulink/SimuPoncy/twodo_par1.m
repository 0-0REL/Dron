%PID parameters
%pidp2or
clc
clear;
close all;

St=0.01; % Tiempo de muestreo 0.01
Tm=St;
SP=1;
LD=1*SP;
Delay=0.00001; %0.4
Kp=12.57;
Ti=0.22*4;
Td=0.04*4;
b=1-0.64;
c=1-0.66;
GE=1;
GCE=2*Td;  %2*Td;0.385
GU=Kp/2;  %Kp/2;4.028
GCU=Kp/Ti;  %Kp/Ti;10.46
stfc22=readfis('stfc22.fis');
stfc23=readfis('stfc23.fis');
p1=3.2;  %3.2;1
q1=3.2;  %3.2;1
p2=0;  %0;1
q2=0;  %0;1
p4=p1;
q4=q1;

Ki=Kp/Ti;
Kd=Kp*Td;
ratio=Td/Ti;
alfa1=(1+sqrt(1^2-4*1*ratio))/2;
alfa2=(1-sqrt(1^2-4*1*ratio))/2;
GCU=Ki;
 
GU=(1-alfa1)*Kp;
GCE=Kd/GU;

GU1=(Kp+sqrt(Kp^2-4*Kd*Ki))/2;
GU2=(Kp-sqrt(Kp^2-4*Kd*Ki))/2;
GCE1=Kd/GU1;
GCE2=Kd/GU2;
% GU=GU2;
% GCE=GCE2;



gk = 9.81; % gravedad
md = 1.6; % masa del dron
Jn = [0.021915027 0.022124548 0.042349865]; % inecia en ejes principales
kf = 0.7*9.81; % coeficiente de empuje
km = 0.2; % coeficiente de arrastre
l = 0.268554; % largo de los brazos
om_0 = sqrt(md*gk/(4*kf)); % velocidad de motores con dron flotando
om_1 = sqrt(md*gk/(4*km)); % velocidad de motores dron rumbo fijo
mk = log(1-0.9933)/-0.1; % retraso motores