%initcond
%Initial conditions for PID autotuning algorithm

%Loads Sampling time (Tm), Delay time (Delay) and the FIS files

%For autotun1
% Tm = 0.04;
% Delay = 0.4;

stfc22 = readfis('stfc22');
stfc23 = readfis('stfc23');
%control_b=readfis('control_b');
%control_c=readfis('control_c');

%For autotune4
% Tm = 0.01;
% Delay = 0;

%stfc4ord = readfis('stfc4ord');


%For two_DF_unsplant1
 Tm = 0.01;
 Delay = 0.5;
fcs_unsplan1=readfis('fcs_unsplan1');