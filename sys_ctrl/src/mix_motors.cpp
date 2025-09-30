// ROS
#include "ros/ros.h"
#include "std_msgs/Float32MultiArray.h"
#include "std_msgs/Float32.h"

float Mr = 0, Mp = 0, My = 0;

void rPIDCallback(const std_msgs::Float32::ConstPtr& msg){
	Mr = msg->data;
}
void pPIDCallback(const std_msgs::Float32::ConstPtr& msg){
	Mp = msg->data;
}
void yPIDCallback(const std_msgs::Float32::ConstPtr& msg){
	My = msg->data;
}

int main(int argc, char **argv){
	// Initialize ROS
	ros::init(argc, argv, "mix_motors");
	ros::NodeHandle nh;
	ros::Publisher ctt_pub = nh.advertise<std_msgs::Float32MultiArray>("motors",1);
	ros::Subscriber rol_sub = nh.subscribe("rl_ctrl", 1, rPIDCallback);
	ros::Subscriber pch_sub = nh.subscribe("pt_ctrl", 1, pPIDCallback);
	ros::Subscriber yaw_sub = nh.subscribe("yw_ctrl", 1, yPIDCallback);
	ros::Rate lr(250);
	// message setup
	std_msgs::Float32MultiArray mot_msg;
	mot_msg.layout.dim.push_back(std_msgs::MultiArrayDimension());
	mot_msg.layout.dim[0].label = "motors";
	mot_msg.layout.dim[0].size = 4;
	mot_msg.layout.dim[0].stride = 4;

	float F = 15.6960;
	float L = 0.268554;
	float kF = 0.7*9.81;
	float kM = 0.05;

	ROS_INFO("mix control motors started");
	while(ros::ok()){
		// mixer
		mot_msg.data.clear();
		mot_msg.data = {
		1000.0f + (-(kM*Mr - kM*Mp - F*L*kM + kF*L*My)/(4*kF*L*kM))*1000.0f,
		1000.0f + (-(kM*Mr + kM*Mp - F*L*kM - kF*L*My)/(4*kF*L*kM))*1000.0f,
		1000.0f + ((kM*Mr - kM*Mp + F*L*kM - kF*L*My)/(4*kF*L*kM))*1000.0f,
		1000.0f + ((kM*Mr + kM*Mp + F*L*kM + kF*L*My)/(4*kF*L*kM))*1000.0f
		};
		ctt_pub.publish(mot_msg);
		ros::spinOnce();
		lr.sleep();
	}
	ROS_INFO("mix motors finished");
	mot_msg.data.clear();
	mot_msg.data = {1000.0, 1000.0, 1000.0, 1000.0};
	ctt_pub.publish(mot_msg);
	return 0;
}
