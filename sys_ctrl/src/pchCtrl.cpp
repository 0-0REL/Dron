// ROS
#include "ros/ros.h"
#include "geometry_msgs/Vector3.h"
#include "std_msgs/Float32.h"
//
#include "iostream"
#include "sys_ctrl/AutoTunePID.h"

float pitch = 0;

void MPUahrsCallback(const geometry_msgs::Vector3::ConstPtr& msg){
	pitch = msg->x;
}

int main(int argc, char **argv){
	// Initialize ROS
	ros::init(argc, argv, "rolCtrl");
	ros::NodeHandle nh;
	ros::Publisher ctt_pub = nh.advertise<std_msgs::Float32>("pch_pid",1);
	ros::Subscriber mpu_sub = nh.subscribe("ahrs_mpu", 1, MPUahrsCallback);
	ros::Rate lr(250);
	// message setup
	std_msgs::Float32 p_msg;
	// PID setup
	float sp = 0.0f;
	AutoTunePID pid(-255,255,TuningMethod::ZieglerNichols);
	pid.setSetpoint(sp); // Set the desired setpoint
	pid.setOscillationMode(OscillationMode::Half); // Set oscillation mode to Half (default steps = 20)
	pid.setOperationalMode(OperationalMode::Tune); // Start in Tune mode for auto-tuning

	std::cout << "pitch control started" << std::endl;
	while(ros::ok()){
		pid.update(pitch);
		float out = pid.getOutput();
		p_msg.data = out;
		ctt_pub.publish(p_msg);
		ros::spinOnce();
		lr.sleep();
	}
	ROS_DEBUG("Gains\nKp: %f\tKi: %f\tKd: %f",pid.getKp(), pid.getKi(), pid.getKd());
	return 0;
}
