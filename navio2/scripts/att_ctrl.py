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
	ctrl_pub = rospy.Publisher('att_ctrl', Float32MultiArray, queue_size=10)
	rospy.Subscriber("ahrs_mpu", Vector3, mpuAHRSCallback)
	rospy.Subscriber("ahrs_lsm", Vector3, lsmAHRSCallback)
	rate = rospy.Rate(250) #frecuencia
	M_pwm = Float32MultiArray()
	rospy.loginfo("SE PRENDIO")
	#pid
	pid_rol = PID(10,3,0,sample_time=None,output_limits=(-500, 500))
	pid_pch = PID(10,3,0,sample_time=None,output_limits=(-500, 500))
	pid_yaw = PID(1,0,0,sample_time=None,output_limits=(-500, 500))
	thro = 1500
	mot = np.array([[1,-1,1,-1], [1,1,1,1], [1,1,-1,-1],[1,-1,-1,1]])
	while not rospy.is_shutdown():
		ahrs = [0.5*MPU[i]+0.5*LSM[i] for i in range(3)]
		m_rol = pid_rol(ahrs[0])
		m_pch = pid_pch(ahrs[1])
		m_yaw = pid_yaw(ahrs[2])
		pwm = np.matmul(mot,np.array([thro,m_rol,m_pch,m_yaw]))
		M_pwm.data = pwm.tolist()
		#str_msg = "Se envia " + str(msg.data[0])+ str(msg.data[1]) + str(msg.data[2] + str.data[3]
		rospy.loginfo("Valores de PWM: %s", str(M_pwm.data))
		ctrl_pub.publish(M_pwm)
		rate.sleep()
if __name__ == '__main__':
	try:
		control_actitud()
	except rospy.ROSInterruptException:
		pass
