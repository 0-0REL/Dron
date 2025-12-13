function xp=Dinamica26(t,x)
%% Estados
% Coordenadas cartesianas
xi_x=x(1,1);  %xi_x
xi_y=x(2,1);  %xi_y
xi_z=x(3,1); % xi_z

xi=[xi_x xi_y xi_z]';
    % Fricción en la dinámica cartesiana.
zxix0=x(4,1);
zxiy0=x(5,1);
zxiz0=x(6,1); 
   % Velocidad de traslación.
xip_x=x(7,1);  %xip_x
xip_y=x(8,1);  %xip_y
xip_z=x(9,1); % xip_z

xip=[xip_x, xip_y, xip_z]';
   
% Orientación
phi=x(10,1);  %phi
theta=x(11,1);  %theta
psi=x(12,1); % psi

eta=[phi, theta, psi]';

    % Fricción en la dinámica rotacional
zphi=x(13,1);
ztheta=x(14,1);
zpsi=x(15,1);
      
    % velocidad de rotación
phip=x(16,1);  %phip
thetap=x(17,1);  %thetap
psip=x(18,1); % psip
 
etap=[phip, thetap, psip]';
   
% Dinámica interna: dinámica en los rotores
omega1=x(19,1); %velocidad rotacional del rotor 1
omega2=x(20,1); %velocidad rotacional del rotor 2
omega3=x(21,1); %velocidad rotacional del rotor 3
omega4=x(22,1); %velocidad rotacional del rotor 4
    % Variables de estado de la fricción en los rotores
z1=x(23,1);   
z2=x(24,1);
z3=x(25,1);
z4=x(26,1);
         
%% Parámetros del dron
I_xx=0.021915027; %momentos de inercia eje x_d
I_yy=0.022124548; %momentos de inercia eje y_d
I_zz=0.042349865; %%momentos de inercia eje z_d
m_d=1.6; %masa del dron.
g=9.81; %contasnte gravitacional.
l_h=0.2794; %longitud de las aspas de las hélices

%% Componentes de la matriz de inercias
m_11=I_zz;
m_12=0;
m_13= I_zz*cos(theta);
m_21=0;
m_22= I_xx*(sin(phi))^2 + I_yy*(cos(phi))^2;
m_23=(I_yy - I_xx)*cos(phi)*sin(phi)*sin(theta);
m_31=m_13;
m_32=m_23;
m_33=(I_xx*(cos(phi))^2+I_yy*(sin(phi))^2)*(sin(theta))^2+I_zz*(cos(theta))^2;

%%%%% Matriz de inercia
M_d=[m_11, m_12, m_13;
    m_21, m_22, m_23;
    m_31,m_32, m_33];

          
%% Componentes de la matriz de Coriolis
c_11=0;

c_12=(I_yy - I_xx)*cos(phi)*sin(phi)*thetap;

c_13=-((I_yy - I_xx)*((cos(phi))^2-(sin(phi))^2)+ I_zz)*sin(theta)*thetap...
          -(I_yy-I_xx)*cos(phi)*sin(phi)*(sin(theta))^2*psip;
      
c_21=-(I_yy- I_xx)*cos(phi)*sin(phi)*thetap;

c_22=-(I_yy- I_xx)*cos(phi)*sin(phi)*phip;

c_23=((I_yy - I_xx)*((cos(phi))^2-(sin(phi))^2)+I_zz)*sin(theta)*phip...
		   -(I_xx*(cos(phi))^2+I_yy*(sin(phi))^2-I_zz)*sin(theta)*cos(theta)*psip;
       
c_31=(I_yy - I_xx)*((cos(phi))^2-(sin(phi))^2)*sin(theta)*thetap...
		 +(I_yy-I_xx)*cos(phi)*sin(phi)*(sin(theta))^2*psip;

c_32=(I_yy - I_xx)*cos(phi)*sin(phi)*cos(theta)*thetap-I_zz*sin(theta)*phip+...
          ((I_xx*(cos(phi))^2 + I_yy*(sin(phi))^2)- I_zz)*cos(theta)*sin(theta)*psip;
                
c_33=(I_yy-I_xx)*cos(phi)*sin(phi)*(sin(theta))^2*phip+...
	       ((I_xx*(cos(phi))^2 + I_yy*(sin(phi))^2)- I_zz)*cos(theta)*sin(theta)*thetap;

       
       
       
%%%%%%% Matriz de Coriolis
 C=[c_11,  c_12, c_13;
	   c_21,  c_22, c_23;
       c_31,  c_32, c_33];    

%%  Esquemas de control
swt_ctrl = 1;
switch swt_ctrl
    case 1 % PD
        [fp_x, fp_y, fp_z, tau_phi, tau_theta, tau_psi]=control_PD(t, xi, xip,  eta, etap);
    case 2 % PID
    case 3 % LQI
    case 4 % Exponencial
    otherwise
        return
end

tau_r1=(1/(4*l_h))*fp_z+(1/4)*tau_phi-(1/2)*tau_theta;                 
tau_r2=(1/(4*l_h))*fp_z-(1/4)*tau_phi-(1/2)*tau_psi;
tau_r3=(1/(4*l_h))*fp_z+(1/4)*tau_phi+(1/2)*tau_theta;
tau_r4=(1/(4*l_h))*fp_z-(1/4)*tau_phi+(1/2)*tau_psi;   
%% Fricción en la dinámica de traslación
%componente en x0
     sigmaxix0_0=0.038;   
     sigmaxix0_1=0.01;
     bxix0=0.1;
     fcxix0=0.54;
     fsxix0=0.62;
    xip_sxix0=5*pi/180;
     muxix0=(fcxix0+(fsxix0-fcxix0)*exp(-abs((xip_x/xip_sxix0)^2)));  
    zpxix0=xip_x-sigmaxix0_0*abs(xip_x)*zxix0/muxix0;
      ffxix0=sigmaxix0_0*zxix0+sigmaxix0_1*zpxix0+bxix0*xip_x;
     
      %componente en y0
      sigmaxiy0_0=0.038;
     sigmaxiy0_1=0.01;
     bxiy0=0.1;
     fcxiy0=0.54;
     fsxiy0=0.62;
    xip_sxiy0=5*pi/180;
     muxiy0=(fcxiy0+(fsxiy0-fcxiy0)*exp(-abs((xip_y/xip_sxiy0)^2)));  
    zpxiy0=xip_y-sigmaxiy0_0*abs(xip_y)*zxiy0/muxiy0;
     ffxiy0=sigmaxiy0_0*zxiy0+sigmaxiy0_1*zpxiy0+bxiy0*xip_y;
     
     %componente en z0
      sigmaxiz0_0=0.038;
     sigmaxiz0_1=0.01;
     bxiz0=0.1;
     fcxiz0=0.54;
     fsxiz0=0.62;
    xip_sxiz0=5*pi/180;
     muxiz0=(fcxiz0+(fsxiz0-fcxiz0)*exp(-abs((xip_z/xip_sxiz0)^2)));  
    zpxiz0=xip_z-sigmaxiz0_0*abs(xip_z)*zxiz0/muxiz0;
     ffxiz0=sigmaxiz0_0*zxiz0+sigmaxiz0_1*zpxiz0+bxiz0*xip_z;
      %%%%%%%%%%% vector de fricción  ffxi
      
      ffxi=[ffxix0;
               ffxiy0;
              ffxiz0];
            
%% Fricción en la dinámica de rotación
%componente en phi
     sigmaphi_0=0.038;   
     sigmaphi_1=0.01;
     bphi=0.08;
     fcphi=0.44;
     fsphi=0.52;
    phip_s=3*pi/180;
     muphi=(fcphi+(fsphi-fcphi)*exp(-abs((phip/phip_s)^2)));  
    zpphi=phip-sigmaphi_0*abs(phip)*zphi/muphi;
      taufphi=sigmaphi_0*zphi+sigmaphi_1*zpphi+bphi*phip;
     
      %componente en theta
     sigmatheta_0=0.038;   
     sigmatheta_1=0.01;
     btheta=0.08;
     fctheta=0.44;
     fstheta=0.52;
    thetap_s=3*pi/180;
     mutheta=(fctheta+(fstheta-fctheta)*exp(-abs((thetap/thetap_s)^2)));  
    zptheta=thetap-sigmatheta_0*abs(thetap)*ztheta/mutheta;
      tauftheta=sigmatheta_0*ztheta+sigmatheta_1*zptheta+btheta*thetap;
     
     %componente en psi
     sigmapsi_0=0.038;   
     sigmapsi_1=0.001;
     bpsi=0.08;
     fcpsi=0.44;
     fspsi=0.52;
    psip_s=3*pi/180;
     mupsi=(fcpsi+(fspsi-fcpsi)*exp(-abs((psip/psip_s)^2)));  
    zppsi=psip-sigmapsi_0*abs(psip)*zpsi/mupsi;
      taufpsi=sigmapsi_0*zpsi+sigmapsi_1*zppsi+bpsi*psip;
      
     tauf=[taufphi;  %vector de torques de fricción en la dinámica rotacional
                tauftheta;
                taufpsi];
%% Fuerza cartesiana en el sistema de referencia fijo 
               fxi=[(fp_x/fp_z)*(1/l_h)*(tau_r1+tau_r2+tau_r3+tau_r4); 
                        (fp_y/fp_z)*(1/l_h)*(tau_r1+tau_r2+tau_r3+tau_r4); 
                      cos(theta)*(1/l_h)*(tau_r1+tau_r2+tau_r3+tau_r4)];

%% Dinámica de traslación
   xipp=(1/m_d)*(fxi-[0;0; m_d*g]-ffxi);
   

   % Torques en la dinámica de orientación
       tau=[tau_r1+tau_r3-tau_r2-tau_r4;
           tau_r3-tau_r1;
         tau_r4-tau_r2];

     
%% Dinámica interna: fricción de los rotores
     sigma1_0=0.0288;
     sigma1_1=0.02;
     b1=0.023;
     Ir1=0.0017;
     fc1=0.3;
     fs1=0.36;
     omega_s1=3*pi/180;
     mu1=(fc1+(fs1-fc1)*exp(-abs((omega1/omega_s1)^2)));  
    zp1=omega1-sigma1_0*abs(omega1)*z1/mu1;
      tauf1=sigma1_0*z1+sigma1_1*zp1+b1*omega1;
      
omegap1=(tau_r1-tauf1)/Ir1;


     sigma2_0=0.0288;
     sigma2_1=0.02;
     b2=0.023;
     Ir2=0.0017;
     fc2=0.3;
     fs2=0.36;
     omega_s2=3*pi/180;
     mu2=(fc2+(fs2-fc2)*exp(-abs((omega2/omega_s2)^2)));  
    zp2=omega2-sigma2_0*abs(omega2)*z2/mu2;
      tauf2=sigma2_0*z2+sigma2_1*zp2+b2*omega2;
      
omegap2=(tau_r2-tauf2)/Ir2;



     sigma3_0=0.0288;
     sigma3_1=0.02;
     b3=0.023;
     Ir3=0.0017;
     fc3=0.3;
     fs3=0.36;
     omega_s3=3*pi/180;
     mu3=(fc3+(fs3-fc3)*exp(-abs((omega3/omega_s3)^2)));  
    zp3=omega3-sigma3_0*abs(omega3)*z3/mu3;
      tauf3=sigma3_0*z3+sigma3_1*zp3+b3*omega3;
      
omegap3=(tau_r3-tauf3)/Ir3;



     sigma4_0=0.0288;
     sigma4_1=0.02;
     b4=0.023;
     Ir4=0.0017;
     fc4=0.3;
     fs4=0.36;
     omega_s4=3*pi/180;
     mu4=(fc4+(fs4-fc4)*exp(-abs((omega4/omega_s4)^2)));  
    zp4=omega4-sigma4_0*abs(omega4)*z4/mu4;
      tauf4=sigma4_0*z4+sigma4_1*zp4+b4*omega4;
      
omegap4=(tau_r4-tauf4)/Ir4;


   %%%%%%%%%% Dinámica de rotación
   etapp=(M_d)^(-1)*(tau-C*etap-tauf);
   


%% Variables de estado ode
xp=[xip(1,1); %velocidad de traslación cartesiana: xi_xp
       xip(2,1); %velocidad de traslación cartesiana: xi_yp
       xip(3,1); %velocidad de traslación cartesiana: xi_zp
       zpxix0; %fricción componte x en la dinámica de traslación
       zpxiy0;%fricción componte y en la dinámica de traslación
       zpxiz0; %fricción componte z en la dinámica de traslación
       xipp(1,1); %aceleración cartesiana en el eje x: xi_xpp
       xipp(2,1); %aceleración cartesiana en el eje y: xi_ypp
       xipp(3,1); %aceleración cartesiana en el eje z: xi_zpp
       etap(1,1); %velocidad rotacional: phip
       etap(2,1); %velocidad rotacional: thetap
       etap(3,1); %velocidad rotacional: psip
       zpphi;       %fricción de la dinámica de rotación: orientación phi
       zptheta;    %fricción de la dinámica de rotación: orientación theta
       zppsi;       %fricción de la dinámica de rotación: orientación psi
       etapp(1,1);%aceleración rotacional: phipp
       etapp(2,1); %aceleración rotacional: thetapp
       etapp(3,1); %aceleración rotacional: psipp
       omegap1;  %dinámica del rotor 1
       omegap2;  %dinámica del rotor 2
       omegap3;  %dinámica del rotor 3
       omegap4;  %dinámica del rotor 4
       zp1;           %dinámica de fricción del rotor 1
       zp2;           %dinámica de fricción del rotor 2
       zp3;           %dinámica de fricción del rotor 3
       zp4            %dinámica de fricción del rotor 4
      ];
end
