// ROS
#include "ros/ros.h"
#include "geometry_msgs/Vector3.h"
#include "std_msgs/Float32.h"
//
#include "iostream"
#include "sys_ctrl/AutoTunePID.h"

float yaw = 0;

void MPUahrsCallback(const geometry_msgs::Vector3::ConstPtr& msg){
	yaw = msg->z;
}

int main(int argc, char **argv){
	// Initialize ROS
	ros::init(argc, argv, "rolCtrl");
	ros::NodeHandle nh;
	ros::Publisher ctt_pub = nh.advertise<std_msgs::Float32>("yaw_pid",1);
	ros::Subscriber mpu_sub = nh.subscribe("ahrs_mpu", 1, MPUahrsCallback);
	ros::Rate lr(250);
	// message setup
	std_msgs::Float32 y_msg;
	// PID setup
	float sp = 0.0f;
	AutoTunePID pid(-100,100,TuningMethod::ZieglerNichols);
	pid.setSetpoint(sp); // Set the desired setpoint
	pid.setOscillationMode(OscillationMode::Mild); // Set oscillation mode to Half (default steps = 20)
	pid.setOperationalMode(OperationalMode::Tune); // Start in Tune mode for auto-tuning

	std::cout << "yaw control started" << std::endl;
	while(ros::ok()){
		pid.update(yaw);
		float out = pid.getOutput();
		y_msg.data = out;
		ctt_pub.publish(y_msg);
		ros::spinOnce();
		lr.sleep();
	}
	ROS_INFO("Gains\nKp: %f\tKi: %f\tKd: %f",pid.getKp(), pid.getKi(), pid.getKd());
	return 0;
}
