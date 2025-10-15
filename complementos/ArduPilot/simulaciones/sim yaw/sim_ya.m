clc; clear;

%% 1. Carga de datos desde .tlog
try
    sim = mavlinktlog("flight.tlog"); 
    attitude_data = readmsg(sim, "MessageName", "ATTITUDE");

    % Extraer todos los yaw y tiempos
    yaw_raw = attitude_data.Messages{1}.yaw * 180/pi;
    time_tlog = attitude_data.Messages{1}.Time;
catch
    error('Error cargando el archivo flight.tlog. ¿Tienes el UAV Toolbox instalado?');
end

%% 2. Carga de datos desde CSV
try
    program_data = readtable('log_prog.csv');

    if ~all(ismember({'timestamp','yaw'}, program_data.Properties.VariableNames))
        error('El archivo CSV debe tener columnas llamadas "timestamp" y "yaw".');
    end

    time_program = program_data.timestamp;
    yaw_program = program_data.yaw;

    if isnumeric(time_program)
        time_program = datetime(time_program, 'ConvertFrom', 'posixtime', 'TimeZone', 'UTC');
    else
        time_program = datetime(time_program, 'TimeZone', 'UTC');
    end
catch
    error('Error cargando el archivo log_prog.csv.');
end

%% 3. Sincronización temporal
time_tlog.TimeZone = '';
time_program.TimeZone = '';

start_time = max(min(time_tlog), min(time_program));
end_time = min(max(time_tlog), max(time_program));

mask_tlog = (time_tlog >= start_time) & (time_tlog <= end_time);
time_tlog_filtered = time_tlog(mask_tlog);
yaw_tlog_filtered = yaw_raw(mask_tlog);

yaw_program_interp = interp1(time_program, yaw_program, time_tlog_filtered, 'linear');

% Calcular tiempo relativo desde el inicio
t_rel = seconds(time_tlog_filtered - start_time);

%% 4. Visualización
figure('Position', [100 100 900 400], 'Color', 'white');

plot(t_rel, yaw_tlog_filtered, 'LineWidth', 1.5, 'Color', [0 0.447 0.741]); hold on;
plot(t_rel, yaw_program_interp, 'LineWidth', 1.5, 'Color', [0.85 0.325 0.098]);

ylabel('Yaw (°)', 'FontSize', 10, 'FontWeight', 'bold');
xlabel('Tiempo (MM:SS)', 'FontSize', 10);
title('Yaw: objetivo vs ejecución', 'FontSize', 12);
grid on;
legend('Yaw (actual)', 'Yaw (objetivo)', 'Location', 'best');

% Formatear eje X como MM:SS
ax = gca;
xticks = ax.XTick;
xticklabels = duration(0, 0, xticks, 'Format', 'mm:ss');
ax.XTickLabel = cellstr(xticklabels);

ax.XAxis.TickLabelRotation = 45;
ax.FontSize = 9;
xlim([0, seconds(end_time - start_time)]);
