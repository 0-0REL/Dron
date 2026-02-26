function Dron= DroneG(dx,dy,dz,ax,ay,az,scale)

scale=0.3*scale;

% dx=1;dy=1;dz=0.5; 
% ax=pi/4;
% ay=pi/4;
az=-pi/2-az;

Rx=[ 1, 0, 0; 0, cos(ax), -sin(ax); 0, sin(ax), cos(ax)];
Ry=[ cos(ay), 0, sin(ay); 0, 1, 0; -sin(ay), 0, cos(ay)];
Rz=[ cos(az), -sin(az), 0; sin(az), cos(az), 0; 0, 0,1];

R=Rx*Ry*Rz;

% cuerpo
cuerpo=[-20.457 -9.917 0;
-8.524 -3.027 0;
-8.524 3.178 0;
-20.457 10.068 0;
-18.882 12.796 0;
-6.884 5.868 0;
-1.575 8.933 0;
-1.575 23.622 0;
1.575 23.622 0;
1.575 8.933 0;
6.884 5.868 0;
20.457 13.705 0;
22.032 10.977 0;
8.524 3.178 0;
8.524 -3.027 0;
22.032 -10.826 0;
20.457 -13.554 0;
7.014 -5.793 0;
1.575 -8.933 0;
1.575 -23.622 0;
-1.575 -23.622 0;
-1.575 -8.933 0;
-7.014 -5.793 0;
-18.882 -12.645 0]*1/(3.937*3);

zb=0.2;

cuerpo1=[cuerpo(:,1) cuerpo(:,2) cuerpo(:,3)+zb];

tam=1;

for k=1:length(cuerpo(:,1))-1
    sp1=[cuerpo(k,1) cuerpo(k,2) cuerpo(k,3);cuerpo(k+1,1) cuerpo(k+1,2) cuerpo(k,3); cuerpo(k+1,1) cuerpo(k+1,2) cuerpo1(k,3); cuerpo(k,1)  cuerpo(k,2) cuerpo1(k,3)]*scale*R;
  Dron(k)=patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,[0.1 0.1 0.1]);
if k==length(cuerpo(:,1))-1
    sp1=[cuerpo(length(cuerpo),1) cuerpo(length(cuerpo),2) cuerpo(k,3); cuerpo(1,1) cuerpo(1,2) cuerpo(k,3); cuerpo(1,1) cuerpo(1,2) cuerpo1(k,3);cuerpo(length(cuerpo),1) cuerpo(length(cuerpo),2) cuerpo1(k,3)]*scale*R;
   Dron(k+1)= patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,[0.1 0.1 0.1]);
end
end

tam=tam+k;
cuerpo=cuerpo*scale*R;
cuerpo1=cuerpo1*scale*R;
Dron(tam+1)=patch(cuerpo(:,1)+dx,cuerpo(:,2)+dy,cuerpo(:,3)+dz,[0.2 0.2 0.2]);
Dron(tam+2)=patch(cuerpo1(:,1)+dx,cuerpo1(:,2)+dy,cuerpo1(:,3)+dz,[0.2 0.2 0.2]);
% cubre elices
a=pi/10;
th=pi/4:a:2*pi+pi/4;

x=1.4142*cos(th)*0.5;
y=1.4142*sin(th)*0.5;
z=0.21*ones(1,length(th));

hp1=[x'+1.7 y'+1 z']*scale*R;
hp2=[x'-1.7 y'+1 z']*scale*R;
hp3=[x'-1.7 y'-1 z']*scale*R;
hp4=[x'+1.7 y'-1 z']*scale*R;
hp5=[x' y'-2 z']*scale*R;
hp6=[x' y'+2 z']*scale*R;

Dron(tam+3)=patch(hp1(:,1)+dx,hp1(:,2)+dy,hp1(:,3)+dz,[0.1 0.1 0.1],'FaceAlpha',0.25);
Dron(tam+4)=patch(hp2(:,1)+dx,hp2(:,2)+dy,hp2(:,3)+dz,[0.1 0.1 0.1],'FaceAlpha',0.25);
Dron(tam+5)=patch(hp3(:,1)+dx,hp3(:,2)+dy,hp3(:,3)+dz,[0.1 0.1 0.1],'FaceAlpha',0.25);
Dron(tam+6)=patch(hp4(:,1)+dx,hp4(:,2)+dy,hp4(:,3)+dz,[0.1 0.1 0.1],'FaceAlpha',0.25);
Dron(tam+7)=patch(hp5(:,1)+dx,hp5(:,2)+dy,hp5(:,3)+dz,[0.1 0.1 0.1],'FaceAlpha',0.25);
Dron(tam+8)=patch(hp6(:,1)+dx,hp6(:,2)+dy,hp6(:,3)+dz,[0.1 0.1 0.1],'FaceAlpha',0.25);

% helices

x=1.4142*cos(th)*0.06;
y=1.4142*sin(th)*0.5;
z=0.22*ones(1,length(th));

h1=[x'+1.7 y'+1 z']*scale*R;
h2=[x'+1.7 y'+1 z']*scale*R;
h3=[x'-1.7 y'+1 z']*scale*R;
h4=[x'-1.7 y'+1 z']*scale*R;

h5=[x'+1.7 y'-1 z']*scale*R;
h6=[x'+1.7 y'-1 z']*scale*R;
h7=[x'-1.7 y'-1 z']*scale*R;
h8=[x'-1.7 y'-1 z']*scale*R;

h9=[x' y'-2 z']*scale*R;
h10=[x' y'-2 z']*scale*R;
h11=[x' y'+2 z']*scale*R;
h12=[x' y'+2 z']*scale*R;


Dron(tam+9)=patch(h1(:,1)+dx,h1(:,2)+dy,h1(:,3)+dz,[0.1 0.1 0.1]);
Dron(tam+10)=patch(h2(:,1)+dx,h2(:,2)+dy,h2(:,3)+dz,[0.1 0.1 0.1]);
Dron(tam+11)=patch(h3(:,1)+dx,h3(:,2)+dy,h3(:,3)+dz,[0.1 0.1 0.1]);
Dron(tam+12)=patch(h4(:,1)+dx,h4(:,2)+dy,h4(:,3)+dz,[0.1 0.1 0.1]);
Dron(tam+13)=patch(h5(:,1)+dx,h5(:,2)+dy,h5(:,3)+dz,[0.1 0.1 0.1]);
Dron(tam+14)=patch(h6(:,1)+dx,h6(:,2)+dy,h6(:,3)+dz,[0.1 0.1 0.1]);
Dron(tam+15)=patch(h7(:,1)+dx,h7(:,2)+dy,h7(:,3)+dz,[0.1 0.1 0.1]);
Dron(tam+16)=patch(h8(:,1)+dx,h8(:,2)+dy,h8(:,3)+dz,[0.1 0.1 0.1]);
Dron(tam+17)=patch(h9(:,1)+dx,h9(:,2)+dy,h9(:,3)+dz,[0.1 0.1 0.1]);
Dron(tam+18)=patch(h10(:,1)+dx,h10(:,2)+dy,h10(:,3)+dz,[0.1 0.1 0.1]);
Dron(tam+19)=patch(h11(:,1)+dx,h11(:,2)+dy,h11(:,3)+dz,[0.1 0.1 0.1]);
Dron(tam+20)=patch(h12(:,1)+dx,h12(:,2)+dy,h12(:,3)+dz,[0.1 0.1 0.1]);


% centro

num_lados=8;
a=360/num_lados*(pi/180);
th=0:a:2*pi;
x=1.4142*cos(th)*0.3;
y=1.4142*sin(th)*0.4;
z=0.05*ones(1,length(th));
zb=0.3;
centro=[x' y' z'];
centro1=[x' y' z'+zb];

num_lados=3;
a=360/num_lados*(pi/180);
th=-pi/2:a:2*pi-pi/2;
x=1.4142*cos(th)*0.15;
y=1.4142*sin(th)*0.15-0.1;
z=0.36*ones(1,length(th));

punto_control=[x' y' z']*scale*R;
Dron(tam+21)=patch(punto_control(:,1)+dx,punto_control(:,2)+dy,punto_control(:,3)+dz,'r');


for k=1:length(centro(:,1))-1
    sp1=[centro(k,1) centro(k,2) centro(k,3);centro(k+1,1) centro(k+1,2) centro(k,3); centro(k+1,1) centro(k+1,2) centro1(k,3); centro(k,1)  centro(k,2) centro1(k,3)]*scale*R;
  Dron(tam+21+k)=patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,[0.1 0.1 0.1]);
if k==length(centro(:,1))-1
    sp1=[centro(length(centro),1) centro(length(centro),2) centro(k,3); centro(1,1) centro(1,2) centro(k,3); centro(1,1) centro(1,2) centro1(k,3);centro(length(centro),1) centro(length(centro),2) centro1(k,3)]*scale*R;
    Dron(tam+21+k+1)=patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,[0.1 0.1 0.1]);
end
end
tam=tam+21+k+1;
centro=centro*scale*R;
centro1=centro1*scale*R;
Dron(tam+1)=patch(centro(:,1)+dx,centro(:,2)+dy,centro(:,3)+dz,[1 1 1]);
Dron(tam+2)=patch(centro1(:,1)+dx,centro1(:,2)+dy,centro1(:,3)+dz,[1 1 1]);
tam=tam+2;
% motores
a=pi/10;
th=pi/4:a:2*pi+pi/4;

x=1.4142*cos(th)*0.15;
y=1.4142*sin(th)*0.15;
z=0*ones(1,length(th));

hp1=[x'+1.7 y'+1 z'];
hp2=[x'-1.7 y'+1 z'];
hp3=[x'-1.7 y'-1 z'];
hp4=[x'+1.7 y'-1 z'];
hp5=[x' y'-2 z'];
hp6=[x' y'+2 z'];

zb=0.21;



for k=1:length(hp1)-1
    sp1=[hp1(k,1) hp1(k,2) 0;hp1(k+1,1) hp1(k+1,2) 0; hp1(k+1,1) hp1(k+1,2) zb; hp1(k,1)  hp1(k,2) zb]*scale*R;
  Dron(tam+k)=patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,'r');
if k==length(hp1)-1
    sp1=[hp1(length(hp1),1) hp1(length(hp1),2) 0; hp1(1,1) hp1(1,2) 0; hp1(1,1) hp1(1,2) zb;hp1(length(hp1),1) hp1(length(hp1),2) zb]*scale*R;
  Dron(tam+k+1)=patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,'r');
end
end
tam=tam+k+1;
for k=1:length(hp2)-1
    sp1=[hp2(k,1) hp2(k,2) 0;hp2(k+1,1) hp2(k+1,2) 0; hp2(k+1,1) hp2(k+1,2) zb; hp2(k,1)  hp2(k,2) zb]*scale*R;
  Dron(tam+k)=patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,'r');
if k==length(hp2)-1
    sp1=[hp2(length(hp2)) hp2(length(hp2),2) 0; hp2(1,1) hp2(1,2) 0; hp2(1,1) hp2(1,2) zb;hp2(length(hp2),1) hp2(length(hp2),2) zb]*scale*R;
  Dron(tam+k+1)=patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,'r');
end
end
tam=tam+k+1;
for k=1:length(hp3)-1
    sp1=[hp3(k,1) hp3(k,2) 0;hp3(k+1,1) hp3(k+1,2) 0; hp3(k+1,1) hp3(k+1,2) zb; hp3(k,1)  hp3(k,2) zb]*scale*R;
  Dron(tam+k)=patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,'r');
if k==length(hp3)-1
    sp1=[hp3(length(hp3)) hp3(length(hp3),2) 0; hp3(1,1) hp3(1,2) 0; hp3(1,1) hp3(1,2) zb;hp3(length(hp3),1) hp3(length(hp3),2) zb]*scale*R;
    Dron(tam+k+1)=patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,'r');
end
end
tam=tam+k+1;
for k=1:length(hp4)-1
    sp1=[hp4(k,1) hp4(k,2) 0;hp4(k+1,1) hp4(k+1,2) 0; hp4(k+1,1) hp4(k+1,2) zb; hp4(k,1)  hp4(k,2) zb]*scale*R;
  Dron(tam+k)=patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,'r');
if k==length(hp4)-1
    sp1=[hp4(length(hp4)) hp4(length(hp4),2) 0; hp4(1,1) hp4(1,2) 0; hp4(1,1) hp4(1,2) zb;hp4(length(hp4),1) hp4(length(hp4),2) zb]*scale*R;
   Dron(tam+k+1)= patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,'r');
end
end
tam=tam+k+1;
for k=1:length(hp5)-1
    sp1=[hp5(k,1) hp5(k,2) 0;hp5(k+1,1) hp5(k+1,2) 0; hp5(k+1,1) hp5(k+1,2) zb; hp5(k,1)  hp5(k,2) zb]*scale*R;
  Dron(tam+k)=patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,'r');
if k==length(hp5)-1
    sp1=[hp5(length(hp5)) hp5(length(hp5),2) 0; hp5(1,1) hp5(1,2) 0; hp5(1,1) hp5(1,2) zb;hp5(length(hp5),1) hp5(length(hp5),2) zb]*scale*R;
   Dron(tam+k+1)= patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,'r');
end
end
tam=tam+k+1;
for k=1:length(hp6)-1
    sp1=[hp6(k,1) hp6(k,2) 0;hp6(k+1,1) hp6(k+1,2) 0; hp6(k+1,1) hp6(k+1,2) zb; hp6(k,1)  hp6(k,2) zb]*scale*R;
  Dron(tam+k)=patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,'r');
if k==length(hp6)-1
    sp1=[hp6(length(hp6)) hp6(length(hp6),2) 0; hp6(1,1) hp6(1,2) 0; hp6(1,1) hp6(1,2) zb;hp6(length(hp6),1) hp6(length(hp6),2) zb]*scale*R;
   Dron(tam+k+1)= patch(sp1(:,1)+dx,sp1(:,2)+dy,sp1(:,3)+dz,'r');
end
end
tam=tam+k+1;

hp1=hp1*scale*R;
hp2=hp2*scale*R;
hp3=hp3*scale*R;
hp4=hp4*scale*R;
hp5=hp5*scale*R;
hp6=hp6*scale*R;


zb=0.21*scale;

Dron(tam+1)=patch(hp1(:,1)+dx,hp1(:,2)+dy,hp1(:,3)+dz,'r');
Dron(tam+2)=patch(hp2(:,1)+dx,hp2(:,2)+dy,hp2(:,3)+dz,'r');
Dron(tam+3)=patch(hp3(:,1)+dx,hp3(:,2)+dy,hp3(:,3)+dz,'r');
Dron(tam+4)=patch(hp4(:,1)+dx,hp4(:,2)+dy,hp4(:,3)+dz,'r');
Dron(tam+5)=patch(hp5(:,1)+dx,hp5(:,2)+dy,hp5(:,3)+dz,'r');
Dron(tam+6)=patch(hp6(:,1)+dx,hp6(:,2)+dy,hp6(:,3)+dz,'r');


Dron(tam+7)=patch(hp1(:,1)+dx,hp1(:,2)+dy,hp1(:,3)+zb+dz,'r');
Dron(tam+8)=patch(hp2(:,1)+dx,hp2(:,2)+dy,hp2(:,3)+zb+dz,'r');
Dron(tam+9)=patch(hp3(:,1)+dx,hp3(:,2)+dy,hp3(:,3)+zb+dz,'r');
Dron(tam+10)=patch(hp4(:,1)+dx,hp4(:,2)+dy,hp4(:,3)+zb+dz,'r');
Dron(tam+11)=patch(hp5(:,1)+dx,hp5(:,2)+dy,hp5(:,3)+zb+dz,'r');
Dron(tam+12)=patch(hp6(:,1)+dx,hp6(:,2)+dy,hp6(:,3)+zb+dz,'r');


pata=[-0 -0.455 0;
4.13 -0.455 -7.154;
4.13 -5.179 -7.154;
4.524 -5.179 -7.835;
4.524 -0.455 -7.835;
4.524 0.455 -7.835;
4.524 5.179 -7.835;
4.13 5.179 -7.154;
4.13 0.455 -7.154;
0 0.455 -0]*1/(3.937*2);

pata(:,1)=pata(:,1)+0.4;

pata=pata*scale*R;

Dron(tam+13)=patch(pata(:,1)+dx,pata(:,2)+dy,pata(:,3)+dz,[0.3 0.3 0.3]);

pata1=[0 -0.455 0;
-4.13 -0.455 -7.154;
-4.13 -5.179 -7.154;
-4.524 -5.179 -7.835;
-4.524 -0.455 -7.835;
-4.524 0.455 -7.835;
-4.524 5.179 -7.835;
-4.13 5.179 -7.154;
-4.13 0.455 -7.154;
0 0.455 -0]*1/(3.937*2);

pata1(:,1)=pata1(:,1)-0.4;

pata1=pata1*scale*R;

Dron(tam+14)=patch(pata1(:,1)+dx,pata1(:,2)+dy,pata1(:,3)+dz,[0.3 0.3 0.3]);

end