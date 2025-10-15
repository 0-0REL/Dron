clc; clear;

%% 1. Carga de datos desde .tlog
try
    sim = mavlinktlog("flight.tlog"); 
    attitude_data = readmsg(sim, "MessageName", "VFR_HUD");

    pitch_raw = attitude_data.Messages{1}.alt;
    time_tlog = attitude_data.Messages{1}.Time;
catch
    error('Error cargando el archivo flight.tlog. ¿Tienes el UAV Toolbox instalado?');
end

%% 2. Carga de datos desde CSV
try
    program_data = readtable('log_prog.csv');

    if ~all(ismember({'timestamp','desp'}, program_data.Properties.VariableNames))
        error('El archivo CSV debe tener columnas llamadas "timestamp" y "desp".');
    end

    time_program = program_data.timestamp;
    distancia_program = program_data.desp;

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
pitch_filtered = pitch_raw(mask_tlog);

distancia_interp = interp1(time_program, distancia_program, time_tlog_filtered, 'linear');

%% 4. Visualización con un solo eje Y y eje X en MM:SS
figure('Position', [100 100 900 400], 'Color', 'white');

relative_time = seconds(time_tlog_filtered - start_time);

plot(relative_time, pitch_filtered-584, 'LineWidth', 1.5, 'Color', [0 0.447 0.741]); hold on;
plot(relative_time, distancia_interp, 'LineWidth', 1.5, 'Color', [0.85 0.325 0.098]);

ylabel('Altura', 'FontSize', 10, 'FontWeight', 'bold');
xlabel('Tiempo (mm:ss)', 'FontSize', 10);
title('Altura actual y objetivo', 'FontSize', 12);
grid on;
legend('Altura (actual)', 'Altura (objetivo)', 'Location', 'best');

% Formato MM:SS en eje X
ax = gca;
xticks = ax.XTick;
xticklabels = string(duration(0, 0, xticks, 'Format','mm:ss'));
ax.XTickLabel = xticklabels;

ax.XAxis.TickLabelRotation = 45;
ax.FontSize = 9;
xlim([0, seconds(end_time - start_time)]);
