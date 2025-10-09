/**
 * @file mix_motors.cpp
 * @author @0-0REL
 * @brief Motor mixing node
 * @version 1.0
 * @date 09-10-2025
 * @details This node mixes the PID outputs to generate PWM signals for the motors
 */
// ROS
#include "ros/ros.h"
#include "std_msgs/Float32MultiArray.h"
#include "std_msgs/Float32.h"

float Mr = 0, Mp = 0, My = 0, F = 0;

// callbacks
void rPIDCallback(const std_msgs::Float32::ConstPtr& msg){
	Mr = msg->data;
}
void pPIDCallback(const std_msgs::Float32::ConstPtr& msg){
	Mp = msg->data;
}
void yPIDCallback(const std_msgs::Float32::ConstPtr& msg){
	My = msg->data;
}
void FCallback(const std_msgs::Float32::ConstPtr& msg){
	F = msg->data;
}

int main(int argc, char **argv){
	// Initialize ROS
	ros::init(argc, argv, "mix_motors");
	ros::NodeHandle nh;
	ros::Publisher pwm_pub = nh.advertise<std_msgs::Float32MultiArray>("motors",1);
	ros::Subscriber rol_sub = nh.subscribe("rl_PID", 1, rPIDCallback);
	ros::Subscriber pch_sub = nh.subscribe("pt_PID", 1, pPIDCallback);
	ros::Subscriber yaw_sub = nh.subscribe("yw_PID", 1, yPIDCallback);
	ros::Subscriber F_sub = nh.subscribe("thrust", 1, FCallback);
	ros::Rate lr(250);	// 250 Hz
	// message setup
	std_msgs::Float32MultiArray mot_msg;
	mot_msg.layout.dim.push_back(std_msgs::MultiArrayDimension());
	mot_msg.layout.dim[0].label = "motors";
	mot_msg.layout.dim[0].size = 4;
	mot_msg.layout.dim[0].stride = 4;

	// Mix motor matrix constants
	constexpr float L = 0.268554;	// length from center to motor (m)
	constexpr float kF = 0.7*9.81;	// thrust coefficient (N/ms)
	constexpr float kM = 0.2;		// moment coefficient (Nm/ms)

	ROS_INFO("mix control motors started");
	while(ros::ok()){
		// mixer
		mot_msg.data.clear();
		mot_msg.data = {
		1000.0f + (-(kM*Mr - kM*Mp - F*L*kM + kF*L*My)/(4*kF*L*kM))*1000.0f,
		1000.0f + (-(kM*Mr + kM*Mp - F*L*kM - kF*L*My)/(4*kF*L*kM))*1000.0f,
		1000.0f + ( (kM*Mr - kM*Mp + F*L*kM - kF*L*My)/(4*kF*L*kM))*1000.0f,
		1000.0f + ( (kM*Mr + kM*Mp + F*L*kM + kF*L*My)/(4*kF*L*kM))*1000.0f
		};
		pwm_pub.publish(mot_msg);
		ros::spinOnce();
		lr.sleep();
	}
	ROS_INFO("mix motors finished");
	mot_msg.data.clear();
	mot_msg.data = {1000.0, 1000.0, 1000.0, 1000.0};
	pwm_pub.publish(mot_msg);
	return 0;
}
