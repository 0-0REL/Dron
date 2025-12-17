from pymavlink import mavutil

class SimpleMav:
    def __init__(self, mode=4):  # 4 = GUIDED mode
        try:
            self.master = mavutil.mavlink_connection('udpin:localhost:14550',input=False,
            source_system=255,
            source_component=0,
            autoreconnect=True,
            retries=3,
            dialect='ardupilotmega',
            robust_parsing=True,
            notimestamps=True)
        except Exception as e:
            print("Error connecting to the vehicle: ", e)
            exit(1)
        self.master.wait_heartbeat()
        self.modov(mode)
        
    def modov(self, modo):
        self.master.mav.set_mode_send(
            self.master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            modo
        )
    def armar(self, armar=1):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            armar,0,0,0,0,0,0
        )
    def despegue(self, altitud=1):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0,0,0,0,0,0,altitud
        )
    def aterrizar(self):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND,
            0,
            0,0,0,0,0,0,0
        )
    def rc_control(self, Roll=65535, Pitch=65535, Throttle=65535, Yaw=65535):
        self.master.mav.rc_channels_override_send(
            self.master.target_system,
            self.master.target_component,
            Roll, Pitch, Throttle, Yaw, 65535, 65535, 65535, 65535
        )
    def intervalo_msg(self, msg_id, f_Hz):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
            getattr(mavutil.mavlink, f'MAVLINK_MSG_ID_{msg_id}'), # The MAVLink message ID
            1e6 / f_Hz, # The interval between two messages in microseconds. Set to -1 to disable and 0 to request default rate.
            0, 0, 0, 0, # Unused parameters
            0, # Target address of message stream (if message has target address fields). 0: Flight-stack default (recommended), 1: address of requestor, 2: broadcast.
        )
    def recibir_msg(self, msg_type):
        return self.master.recv_match(type=msg_type, blocking=True, timeout=0.1)
    def fin(self):
        self.master.close()