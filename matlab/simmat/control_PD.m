function u = control_PD(h, actual, anterior)
kP = [1 ...
    0.53 0.54 1.02]';
kD = [2 ...
    0.20 0.20 0.38]';

u = (kP+kD/h)*actual - kD*h*anterior;
end