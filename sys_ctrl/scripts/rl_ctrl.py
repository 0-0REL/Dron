#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float32
from geometry_msgs.msg import Vector3
#
from simple_pid import PID

MPU = [0, 0, 0]
LSM = [0, 0, 0]

def mpuAHRSCallback(msg):
        MPU[:] = [msg.x, msg.y, msg.z]
def lsmAHRSCallback(msg):
        LSM[:] = [msg.x, msg.y, msg.z]

def control_actitud():
        #ros
        rospy.init_node('rl_ctrl', anonymous=False)
        rTpub = rospy.Publisher('mix_motors', Float32, queue_size=1)
        rospy.Subscriber("ahrs_mpu", Vector3, mpuAHRSCallback)
        #rospy.Subscriber("ahrs_lsm", Vector3, lsmAHRSCallback)
        rate = rospy.Rate(250) #frecuencia
        Mr = Float32()
        rospy.loginfo("SE PRENDIO roll")
        #pid
        pid_rol = PID(0.768458, 0, 0.123034,sample_time=None)
        while not rospy.is_shutdown():
                #ahrs = [1.0*MPU[i]+0.0*LSM[i] for i in range(3)]
                ahrs = 1.0*MPU[1]+0.0*LSM[1]
                Mr.data = pid_rol(ahrs)
                rTpub.publish(Mr)
                rate.sleep()

if __name__ == '__main__':
        try:
                control_actitud()
        except rospy.ROSInterruptException:
                Mr.data = 0
                rTpub.publish(Mr)
