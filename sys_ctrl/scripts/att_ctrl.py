#!/usr/bin/env python3
#ros
import rospy
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Vector3
#
from simple_pid import PID

MPU = [0, 0, 0]
LSM = [0, 0, 0]

def mpuAHRSCallback(msg):
	MPU[:] = [msg.x, msg.y, msg.z]
def lsmAHRSCallback(msg):
	LSM[:] = [msg.x, msg.y, msg.z]

def pulsos(F=0, Mr=0, Mp=0, My=0):
	'''
	Convert moments to signals for motors.
	Args:
		F: Total motors force.
		Mr: Moment in roll.
		Mp: Moment in Pitch.
		My: Moment in Yaw.
	Returns:
		Signal for each motor.
	'''
	L = 0.268554
	kF = 0.7*9.81
	kM = 0.02
	signal = [0, 0, 0, 0]
	signal[0] = 1000.0 + (-(kM*Mr - kM*Mp - F*L*kM + kF*L*My)/(4*kF*L*kM))*1000.0
	signal[1] = 1000.0 + (-(kM*Mr + kM*Mp - F*L*kM - kF*L*My)/(4*kF*L*kM))*1000.0
	signal[2] = 1000.0 + ((kM*Mr - kM*Mp + F*L*kM - kF*L*My)/(4*kF*L*kM))*1000.0
	signal[3] = 1000.0 + ((kM*Mr + kM*Mp + F*L*kM + kF*L*My)/(4*kF*L*kM))*1000.0
	return signal

M_pwm = Float32MultiArray()
def control_actitud():
	
	rospy.loginfo("Attitude controller started")
	#pid
	pid_rol = PID(0.206485, 0, 0.076489, sample_time=None)
	pid_pch = PID(0.212170, 0, 0.078595, sample_time=None)
	pid_yaw = PID(0.401057, 0, 0.148564, sample_time=None)

	i = 0
	Fh = 0
	while not rospy.is_shutdown():
		ahrs = [1.0*MPU[i]+0.0*LSM[i] for i in range(3)]
		Mroll = pid_rol(ahrs[1])
		Mpitch = pid_pch(ahrs[0])
		Myaw = pid_yaw(ahrs[2])
		Fh = i*15.696/1000
		if Fh >= 15.696:
			Fh = 15.696
		else:
			i = i + 1
		#Fh = 15.6960 # Hover thrust
		pMot = pulsos(Fh, Mroll, Mpitch, Myaw)
		M_pwm.data = pMot
		ctrl_pub.publish(M_pwm)
		rate.sleep()
if __name__ == '__main__':
	try:
		#ros
		rospy.init_node('stblz', anonymous=False)
		ctrl_pub = rospy.Publisher('motors', Float32MultiArray, queue_size=1)
		rospy.Subscriber("ahrs_mpu", Vector3, mpuAHRSCallback)
		#rospy.Subscriber("ahrs_lsm", Vector3, lsmAHRSCallback)
		rate = rospy.Rate(500) #frecuencia
		control_actitud()
	except rospy.ROSInterruptException:
		pMot = [1000, 1000, 1000, 1000]
		M_pwm.data = pMot
		ctrl_pub.publish(M_pwm)
