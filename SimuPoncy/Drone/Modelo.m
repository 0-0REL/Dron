clc
clear all
close all

ts=0.1;
t=0:ts:10;
a=0.1;

% 1. Condiciones iniciales
        xc(1) = 0;              %pocisión en el eje x en (m)
        yc(1) = 0;              %pocisión en el eje y en (m)
        zr(1) = 0;              %pocisión en el eje z en (m)
        
 
        phi(1)= 0*(pi/180);     %orientación en radianes 
    

        xr(1)=xc(1)+a*cos(phi(1));
        yr(1)=yc(1)+a*sin(phi(1));

% 3) Referencias deseadas
        xrd = -2;
        yrd = 2;
        zrd = 5;
        phid=90*(pi/180);
  
for k=1:length(t)
    
    %a) Errores de control
    xre(k) = xrd - xr(k);
    yre(k) = yrd - yr(k);
    zre(k) = zrd - zr(k);
    phie(k) = phid-phi(k);
    
    e = [xre(k);yre(k);zre(k);phie(k)];
    
    %b) Matriz Jacobiana
    J=[cos(phi(k)) -sin(phi(k))   0 -a*sin(phi(k));...
       sin(phi(k))  cos(phi(k))   0  a*cos(phi(k));...
        0           0             1           0;...
        0           0             0           1];
       
    %c) Matriz de ganancia
    K = [0.1 0 0 0;...
         0 0.1 0  0;...
         0 0 0.5 0;...
         0 0 0 0.5];

    %d) Ley de control    
    v = inv(J)*K*e;
    
    uf(k)=v(1);
    ul(k)=v(2);
    uz(k)=v(3);
    w(k)=v(4);
    
    
    
    
    xrp(k)=uf(k)*cos(phi(k))-ul(k)*sin(phi(k))-a*w(k)*sin(phi(k));
    yrp(k)=uf(k)*sin(phi(k))+ul(k)*cos(phi(k))+a*w(k)*cos(phi(k));
    zrp(k)=uz(k);
    
    xr(k+1)=xr(k)+ts*xrp(k);
    yr(k+1)=yr(k)+ts*yrp(k);
    zr(k+1)=zr(k)+ts*zrp(k);
    
    phi(k+1)=phi(k)+ts*w(k);
    
    
    
    xc(k+1)=xr(k+1)-a*cos(phi(k+1));
    yc(k+1)=yr(k+1)-a*sin(phi(k+1));
    
end


pasos=5;  fig=figure;
set(fig,'position',[10 60 980 600]);
axis square; cameratoolbar
grid on;
axis([-3 3 -3 3 0 7]); grid on

M1=Drone6(xc(1),yc(1),zr(1),0,0,phi(1),1);

hold on, plot3(xr,yr,zr);

for i=1:pasos:length(t)
    
    delete (M1)
    M1=Drone6(xc(i),yc(i),zr(i),0,0,phi(i),1);
    
    pause(0.1)
    
end

%% Graficas
figure('Name','Errores')
subplot(411)
plot(t,xre,'linewidth',2), grid on
legend('Error en x')
xlabel('Tiempo'), ylabel('Error  [m]')
subplot(412)
plot(t,yre,'g','linewidth',2), grid on
legend('Error en y')
xlabel('Tiempo'), ylabel('Error  [m]')
subplot(414)
plot(t,phie,'g','linewidth',2), grid on
legend('Error en phi')
xlabel('Tiempo'), ylabel('Error  [rad]')
subplot(413)
plot(t,zre,'g','linewidth',2), grid on
legend('Error en z')
xlabel('Tiempo'), ylabel('Error  [m]')

figure('Name','Acciones de control')
subplot(411)
plot(t,uf,'linewidth',2), grid on
legend('Velocidad lineal frontal uf')
xlabel('Tiempo'), ylabel('Velocidad [m/s]')
subplot(412)
plot(t,ul,'g','linewidth',2), grid on
legend('Velocidad lineal lateral ul')
xlabel('Tiempo'), ylabel('Velocidad  [m/s]')
subplot(413)
plot(t,uz,'g','linewidth',2), grid on
legend('Velocidad z')
xlabel('Tiempo'), ylabel('Velocidad  [m/s]')
subplot(414)
plot(t,w,'g','linewidth',2), grid on
legend('Velocidad angular w')
xlabel('Tiempo'), ylabel('Velocidad  [rad/s]')
