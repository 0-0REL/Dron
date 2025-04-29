# Prueba de conexión con el vehículo

#from pymavlink import mavutil
from pymavlink import mavutil

# Start a connection listening on a UDP port
try:
    connection = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
except Exception as e:
    print("Error connecting to the vehicle: ", e)
    exit(1)
# Wait for the first heartbeat to set the system and component ID of remote system for the link
connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))