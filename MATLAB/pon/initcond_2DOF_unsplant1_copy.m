%initcond_2DOF_delay0dot2
%Initial conditions for PID autotuning algorithm

clear all;
close all;

%Loads Sampling time (Tm), Delay time (Delay) and the FIS files

%For two_DF_unsplant1
Tm = 0.001;
Delay = 0.005;
fcs_unsplan1=readfis('fcs_unsplan1');

stfc22 = readfis('stfc22');
stfc23 = readfis('stfc23');