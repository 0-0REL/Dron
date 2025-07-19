clc; clear;
%% 1. Carga de datos desde .tlog
try
    sim = mavlinktlog("flight.tlog"); 
    attitude_data = readmsg(sim, "MessageName", "ATTITUDE");

    % Extraer todos los pitch y tiempos
    pitch_raw = attitude_data.Messages{1}.pitch * 180/pi;
    time_tlog = attitude_data.Messages{1}.Time;
catch
    error('Error cargando el archivo flight.tlog. ¿Tienes el UAV Toolbox instalado?');
end

%% 2. Carga de datos desde CSV
try
    program_data = readtable('log_vx_yaw_vz.csv');

    % Validación de nombres de columnas
    if ~all(ismember({'timestamp','distancia'}, program_data.Properties.VariableNames))
        error('El archivo CSV debe tener columnas llamadas "timestamp" y "distancia".');
    end

    time_program = program_data.timestamp;
    distancia_program = program_data.distancia;

    % Convertir a datetime si es numérico
    if isnumeric(time_program)
        time_program = datetime(time_program, 'ConvertFrom', 'posixtime', 'TimeZone', 'UTC');
    else
        time_program = datetime(time_program, 'TimeZone', 'UTC');
    end
catch
    error('Error cargando el archivo log_vx_yaw_vz.csv.');
end

%% 3. Sincronización temporal
time_tlog.TimeZone = '';
time_program.TimeZone = '';

% Rango común
start_time = max(min(time_tlog), min(time_program));
end_time = min(max(time_tlog), max(time_program));

% Filtrado
mask_tlog = (time_tlog >= start_time) & (time_tlog <= end_time);
time_tlog_filtered = time_tlog(mask_tlog);
pitch_filtered = pitch_raw(mask_tlog);

% Interpolación
distancia_interp = interp1(time_program, distancia_program, time_tlog_filtered, 'linear');

%% 4. Visualización (con eje en MM:SS desde el inicio)
figure('Position', [100 100 900 400], 'Color', 'white');

% Calcular tiempos relativos en segundos desde el inicio
relative_time = seconds(time_tlog_filtered - start_time);

% Subplot con eje doble
yyaxis left;
plot(relative_time, pitch_filtered, 'LineWidth', 1.5, 'Color', [0 0.447 0.741]);
ylabel('Pitch (°)', 'FontSize', 10, 'FontWeight', 'bold');

yyaxis right;
plot(relative_time, distancia_interp / 30, 'LineWidth', 1.5, 'Color', [0.85 0.325 0.098]);
ylabel('Distancia (m)', 'FontSize', 10, 'FontWeight', 'bold');

title('Distancia vs respuesta en pitch', 'FontSize', 12);
xlabel('Tiempo (mm:ss)', 'FontSize', 10);
grid on;
legend('Pitch', 'Distancia', 'Location', 'best');

% Formato del eje X en MM:SS
ax = gca;
xticks = ax.XTick;
xticklabels = string(duration(0, 0, xticks, 'Format','mm:ss'));
ax.XTickLabel = xticklabels;

ax.XAxis.TickLabelRotation = 45;
ax.FontSize = 9;
xlim([0, seconds(end_time - start_time)]);