#!/usr/bin/env python3
#ros
import rospy
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Vector3
#
from simple_pid import PID
import numpy as np

MPU = [0, 0, 0]
LSM = [0, 0, 0]

def mpuAHRSCallback(msg):
	MPU[:] = [msg.x, msg.y, msg.z]
def lsmAHRSCallback(msg):
	LSM[:] = [msg.x, msg.y, msg.z]
def control_actitud():
	#ros
	rospy.init_node('stblz', anonymous=True)
	ctrl_pub = rospy.Publisher('att_ctrl', Float32MultiArray, queue_size=1)
	rospy.Subscriber("ahrs_mpu", Vector3, mpuAHRSCallback)
	#rospy.Subscriber("ahrs_lsm", Vector3, lsmAHRSCallback)
	rate = rospy.Rate(250) #frecuencia
	M_pwm = Float32MultiArray()
	rospy.loginfo("SE PRENDIO")
	#pid
	pid_rol = PID(5,0,0,sample_time=None,output_limits=(-150, 150))
	pid_pch = PID(5,0,0,sample_time=None,output_limits=(-150, 150))
	pid_yaw = PID(0,0,0,sample_time=None,output_limits=(-150, 150))
	thro = 1320
	mot = np.array([[1,-1,1,-1],
				 [1,1,-1,-1],
				 [1,-1,-1,1],
				 [1,1,1,1]])
	while not rospy.is_shutdown():
		ahrs = [1.0*MPU[i]+0.0*LSM[i] for i in range(3)]
		m_rol = pid_rol(ahrs[1])
		m_pch = pid_pch(ahrs[0])
		#m_yaw = pid_yaw(ahrs[2])
		m_yaw = 0
		pwm = mot @ np.array([thro, m_yaw, m_pch, m_rol])
		M_pwm.data = pwm.tolist()
		#rospy.loginfo(f"PID roll: {m_rol:.2f} pitch: {m_pch:.2f} yaw: {m_yaw:.2f}")
		#rospy.loginfo(f"Valores de PWM: {M_pwm.data[0]:.2f} {M_pwm.data[1]:.2f} {M_pwm.data[2]:.2f} {M_pwm.data[3]:.2f}")
		ctrl_pub.publish(M_pwm)
		rate.sleep()
if __name__ == '__main__':
	try:
		control_actitud()
	except rospy.ROSInterruptException:
		pass
