// ROS
#include "ros/ros.h"
#include "std_msgs/Float32MultiArray.h"
#include "std_msgs/Float32.h"
//
#include "iostream"
#include "sys_ctrl/AutoTunePID.h"

float rPID = 0, pPID = 0, yPID = 0;

void rPIDCallback(const std_msgs::Float32::ConstPtr& msg){
	rPID = msg->data;
}
void pPIDCallback(const std_msgs::Float32::ConstPtr& msg){
	pPID = msg->data;
}
void yPIDCallback(const std_msgs::Float32::ConstPtr& msg){
	yPID = msg->data;
}

int main(int argc, char **argv){
	// Initialize ROS
	ros::init(argc, argv, "mixCtrl");
	ros::NodeHandle nh;
	ros::Publisher ctt_pub = nh.advertise<std_msgs::Float32MultiArray>("motors",1);
	ros::Subscriber rol_sub = nh.subscribe("rol_pid", 1, rPIDCallback);
    ros::Subscriber pch_sub = nh.subscribe("pch_pid", 1, pPIDCallback);
    ros::Subscriber yaw_sub = nh.subscribe("yaw_pid", 1, yPIDCallback);
	ros::Rate lr(250);
    // message setup
    std_msgs::Float32MultiArray mot_msg;
	mot_msg.layout.dim.push_back(std_msgs::MultiArrayDimension());
	mot_msg.layout.dim[0].label = "motors";
	mot_msg.layout.dim[0].size = 4;
	mot_msg.layout.dim[0].stride = 4;

    int b_thro = 1550;

    std::cout << "mix control motors started" << std::endl;
    while(ros::ok()){
        // mixer
        mot_msg.data.clear();
        mot_msg.data = {
            b_thro-rPID+pPID-yPID,
            b_thro-rPID-pPID+yPID,
            b_thro+rPID-pPID-yPID,
            b_thro+rPID+pPID+yPID
        };
        ctt_pub.publish(mot_msg);
        ros::spinOnce();
        lr.sleep();
    }
    std::cout << "motors stopped" << std::endl;
    mot_msg.data.clear();
    mot_msg.data = {1000.0, 1000.0, 1000.0, 1000.0};
    ctt_pub.publish(mot_msg);
    return 0;
}
