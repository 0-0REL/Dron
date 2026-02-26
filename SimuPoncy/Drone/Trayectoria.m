clc
clear all
close all

ts=0.1;
t=0:ts:60;
a=0.1;

% 1. Condiciones iniciales
        xc(1) = 0;              %pocisión en el eje x en (m)
        yc(1) = 0;              %pocisión en el eje y en (m)
        zr(1) = 0;              %pocisión en el eje z en (m)
        
 
        phi(1)= 0*(pi/180);     %orientación en radianes 
    

        xr(1)=xc(1)+a*cos(phi(1));
        yr(1)=yc(1)+a*sin(phi(1));

% 2) Referencias deseadas
%         xrd = 2.5*cos(0.2*t);
%         yrd = 2.5*sin(0.2*t);
%         zrd = 7*ones(1,length(t));
%         
%         phid=45*ones(1,length(t))*(pi/180);
%         
%         xrd_p= -2.5*0.2*sin(0.2*t);
%         yrd_p= 2.5*0.2*cos(0.2*t);
%         zrd_p= 0*ones(1,length(t));
%                 
%         phid_p=zeros(1,length(t));
% 
%         xrd = 2.5*cos(0.2*t);
%         yrd = 2.5*sin(0.4*t);
%         zrd = 7*ones(1,length(t));
%         
%         phid=45*ones(1,length(t))*(pi/180);
%         
%         xrd_p= -2.5*0.2*sin(0.2*t);
%         yrd_p= 2.5*0.4*cos(0.4*t);
%         zrd_p= 0*ones(1,length(t));
%                 
%         phid_p=zeros(1,length(t));
%         

        xrd = 2.5*cos(0.2*t);
        yrd = 2.5*sin(0.2*t);
        zrd = 0.1*t;
        
        phid=90*ones(1,length(t))*(pi/180);
        
        xrd_p= -2.5*0.2*sin(0.2*t);
        yrd_p= 2.5*0.2*cos(0.2*t);
        zrd_p= 0.1*ones(1,length(t));
                
        phid_p=zeros(1,length(t));

  
for k=1:length(t)
    
    %a) Errores de control
    xre(k) = xrd(k) - xr(k);
    yre(k) = yrd(k) - yr(k);
    zre(k) = zrd(k) - zr(k);
    
    phie(k) = phid(k)-phi(k);
    
    e = [xre(k);yre(k);zre(k);phie(k)];
   
    
    %b) Matriz Jacobiana
    J=[cos(phi(k)) -sin(phi(k))   0 -a*sin(phi(k));...
       sin(phi(k))  cos(phi(k))   0  a*cos(phi(k));...
        0           0             1           0;...
        0           0             0           1];
       
    %c) Matriz de ganancia
    K = [1 0 0 0;...
         0 5 0 0;...
         0 0 1 0;...
         0 0 0 1];

    hd_p=[xrd_p(k) yrd_p(k) zrd_p(k) phid_p(k)]';
    
    %d) Ley de control  
    v = inv(J)*(hd_p+K*tanh(e));
  
    
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
axis([-3 3 -3 3 0 9]); grid on

M1=Drone6(xc(1),yc(1),zr(1),0,0,phi(1),1);

hold on, plot3(xrd,yrd,zrd,'g');

for i=1:pasos:length(t)
    
    delete (M1)
    M1=Drone6(xc(i),yc(i),zr(i),0,0,phi(i),1);
    plot3(xr(1:i),yr(1:i),zr(1:i));
    
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
