from pymavlink import mavutil

try:
    #connection = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
    #dron_conec = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
    dron_conec = mavutil.mavlink_connection('udpin:localhost:14550')
except Exception as e:
    print("Error connecting to the vehicle: ", e)
    exit(1)

dron_conec.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (dron_conec.target_system, dron_conec.target_component))
dron_conec.mav.set_mode_send(
    dron_conec.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    4 # 4 = GUIDED
)

dron_conec.mav.command_long_send(
        dron_conec.target_system,
        dron_conec.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1, 0, 0, 0, 0, 0, 0
)

while True:
    dron_conec.mav.rc_channels_override_send(
        dron_conec.target_system,
        dron_conec.target_component,
        65535, 65535, 1150, 65535, 65535, 65535, 65535, 65535
    )
