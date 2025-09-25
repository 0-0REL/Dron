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
	Convierte momentos a señales para los motores.
	Args:
		F: Fuerza total de los motores.
        Mr: Momento en Roll.
		Mp: Momento en Pitch.
		My: Momento en Yaw.
    Returns:
        Señales para cada motor en porcentaje.
	'''
	L = 0.268554;
	kF = 0.7*9.81;
	kM = 0.05;
	signal = [0, 0, 0, 0]
	signal[0] = 1000.0 + (-(kM*Mr - kM*Mp - F*L*kM + kF*L*My)/(4*kF*L*kM))*1000.0
	signal[1] = 1000.0 + (-(kM*Mr + kM*Mp - F*L*kM - kF*L*My)/(4*kF*L*kM))*1000.0
	signal[2] = 1000.0 + ((kM*Mr - kM*Mp + F*L*kM - kF*L*My)/(4*kF*L*kM))*1000.0
	signal[3] = 1000.0 + ((kM*Mr + kM*Mp + F*L*kM + kF*L*My)/(4*kF*L*kM))*1000.0
	return signal
def control_actitud():
	#ros
	rospy.init_node('stblz', anonymous=False)
	ctrl_pub = rospy.Publisher('motors', Float32MultiArray, queue_size=1)
	rospy.Subscriber("ahrs_mpu", Vector3, mpuAHRSCallback)
	#rospy.Subscriber("ahrs_lsm", Vector3, lsmAHRSCallback)
	rate = rospy.Rate(250) #frecuencia
	M_pwm = Float32MultiArray()
	rospy.loginfo("SE PRENDIO")
	#pid
	pid_rol = PID(0.768458, 0, 0.123034,sample_time=None)
	pid_pch = PID(0.789616, 0, 0.126421,sample_time=None)
	#pid_yaw = PID(0, 0, 0,sample_time=None,output_limits=(0, 1))

	while not rospy.is_shutdown():
		ahrs = [1.0*MPU[i]+0.0*LSM[i] for i in range(3)]
		Mroll = pid_rol(ahrs[1])
		Mpitch = pid_pch(ahrs[0])
		#m_yaw = pid_yaw(ahrs[2])
		Fh = 15.6960 # Fuerza de hover
		pMot = pulsos(Fh, Mroll, Mpitch)
		M_pwm.data = pMot
		#rospy.loginfo(f"PID roll: {m_rol:.2f} pitch: {m_pch:.2f} yaw: {m_yaw:.2f}")
		#rospy.loginfo(f"Valores de PWM: {M_pwm.data[0]:.2f} {M_pwm.data[1]:.2f} {M_pwm.data[2]:.2f} {M_pwm.data[3]:.2f}")
		ctrl_pub.publish(M_pwm)
		rate.sleep()
if __name__ == '__main__':
	try:
		control_actitud()
	except rospy.ROSInterruptException:
		pMot = [1000, 1000, 1000, 1000]
		M_pwm.data = pMot
		ctrl_pub.publish(M_pwm)
