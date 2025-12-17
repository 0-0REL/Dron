function dx = Dinamica12(t,x)
     % 12 Estados modelo clasico sobre marco de referencia
X = x(1); Y = x(2); Z = x(3);
dX = x(4); dY = x(5); dZ = x(6);
phi = x(7); theta = x(8); psi = x(9);
dphi = x(10); dtheta = x(11); dpsi = x(12);

    % Parametros del dron
Jn = diag([0.021915027 0.022124548 0.042349865]); % Momentos principales
m = 1.6;              % Masa del dron.
g = 9.81;             % Contasnte gravitacional.
L = 0.2794;           % Longitud de las aspas de las hélices
kF = 0.7*9.81;
kM = 0.5;
h = 1/512;% Muestreo para controlador

    % Controlador (discreto)
e(1) = 1 - Z;
e(2) = 0 - phi;
e(3) = 0 - theta;
e(4) = 0 - psi;
%u = control_PD(h,act,prev);

k = [2.828427124746216e+02	9.383923531230010e-13	-1.210270100962480e-12	4.345744931291718e-12	2.184130804814352e+02	75.491203842173974	-7.709307526261328e-13	5.256191100560787e-13	1.870486458131408e-12	-1.008768142932351e-13	-3.237421760483896e-14	-5.433466457111888e-14;
2.346449781332746e-13	2.236067977499710e+03	3.425452774142774e-11	2.761675223592869e-11	1.045397976255164e-13	-4.224431920439947e-14	2.101348922492393e+03	1.290939714248262e-11	9.535728313185168e-12	5.401596280541262e+02	7.821059629283724e-13	6.255242936692398e-13;
2.571673124274038e-13	-4.149365835300502e-11	2.236067977499747e+03	-1.135847164050849e-11	2.031052989324331e-13	7.279679632954474e-14	-1.245008253682494e-11	2.099380513628321e+03	-1.332293920906762e-13	-1.763347326278887e-12	5.383106786615103e+02	-7.366201056273448e-14;
6.401008972992898e-13	5.026465546285799e-11	-4.627843544826754e-11	2.236067977499764e+03	6.668418917005138e-13	2.369777279705387e-13	2.010880867537750e-11	-1.708991907901855e-11	1.992555605095314e+03	2.559167039417501e-12	-1.835800974480607e-12	4.405675183452637e+02];
F = m*g;
tau = zeros(3,1);

A = [kF kF kF kF;
    -L*kF -L*kF L*kF L*kF;
    L*kF -L*kF -L*kF L*kF;
    -kM kM -kM kM];
ms = A\[F; tau];

    % Dinamica traslacion
ddr = ([0;0;-m*g] + [sin(theta)*cos(psi) + sin(phi)*cos(theta)*sin(psi); ...
                    sin(theta)*sin(psi) - sin(phi)*cos(theta)*cos(psi); ...
                    cos(phi)*cos(theta)])*F/m;
   % Dinamica de rotacion
Ir = [Jn(1,1)*cos(theta) 0 -Jn(1,1)*cos(phi)*sin(theta);
    0 Jn(2,2) Jn(2,2)*sin(phi);
    Jn(3,3)*sin(theta) 0 Jn(3,3)*cos(phi)*cos(theta)];
k(1,1) = (Jn(1,1)+Jn(2,2)-Jn(3,3))*dphi*dtheta*sin(theta) + (-Jn(1,1)+Jn(2,2)-Jn(3,3))*dphi*dpsi*sin(phi)*sin(theta) + (Jn(1,1)+Jn(2,2)-Jn(3,3))*dtheta*dpsi*cos(phi)*cos(theta) + (Jn(2,2)-Jn(3,3))*power(dpsi,2)*sin(phi)*cos(phi)*cos(theta);
k(2,1) = (-Jn(2,2)+(-Jn(1,1)+Jn(3,3))*cos(2*theta))*dphi*dpsi*cos(phi) + (-Jn(1,1)+Jn(3,3))*(power(dphi,2)-power(dpsi*cos(phi),2))*sin(theta)*cos(theta);
k(3,1) = (Jn(1,1)-Jn(2,2)-Jn(3,3))*dphi*dtheta*cos(theta) + (Jn(1,1)-Jn(2,2)+Jn(3,3))*dphi*dpsi*sin(phi)*cos(theta) + (-Jn(1,1)+Jn(2,2)+Jn(3,3))*dtheta*dpsi*cos(dphi)*sin(theta) + (-Jn(1,1)+Jn(2,2))*power(dpsi,2)*sin(phi)*cos(phi)*sin(theta);
ddeta = Ir\(k + tau);
% velociad angular en cuerpo
omega = [cos(theta) 0 -cos(phi)*sin(theta);
    0 1 sin(phi);
    sin(theta) 0 cos(phi)*cos(theta)]*[dphi;dtheta;dpsi];
dx = [dX;
    dY;
    dZ;
    ddr;
    omega;
    ddeta];
end