/**
 * @file att_ctrl.cpp
 * @author @0-0REL
 * @brief Attitude controller node
 * @version 1.0
 * @date 20-10-2025
 * @details PID controller for roll, pitch  and yaw angles
 */
// ROS
#include "ros/ros.h"
#include "geometry_msgs/Vector3.h"
//
#include "sys_ctrl/cmon-pid.h"

float roll = 0;
float pitch = 0;
float yaw = 0;

void MPUahrsCallback(const geometry_msgs::Vector3::ConstPtr& msg){
        pitch = msg->x;
        roll = msg->y;
        yaw = msg->z;
}

int main(int argc, char **argv){
	// Initialize ROS
	ros::init(argc, argv, "att_ctrl");
	ros::NodeHandle nh;
	ros::Publisher ctt_pub = nh.advertise<geometry_msgs::Vector3>("T_ctrl",1);
	ros::Subscriber mpu_sub = nh.subscribe("ahrs_mpu", 1, MPUahrsCallback);
	ros::Rate r(500);
	// message setup
	geometry_msgs::Vector3 c_msg;

	// PID setup
	clamping_t<pid_bwe> c_roll;
    clamping_t<pid_bwe> c_pitch;
    clamping_t<pid_bwe> c_yaw;
    constexpr float h = 1.0/500.0;
    // ROLL 
	c_roll.ParallelPid(h, 0.206485, 0, 0.076489, h/2);
	//c_roll.NStandardPid(h, 0.0646, 11.3257, 1.9056, 2.7963e3);
	c_roll.Clamping(-1.0,1.0);
	c_roll.SteadyStateInit(0);
    // PITCH
	c_pitch.ParallelPid(h, 0.212170, 0, 0.078595, h/2;
	//c_pitch.NStandardPid(h, 0.0663, 11.3257, 1.9056, 2.7963e3);
	c_pitch.Clamping(-1.0,1.0);
	c_pitch.SteadyStateInit(0);
    // YAW
	c_yaw.ParallelPid(h, 0.401057, 0, 0.148564, h/2);
	//c_yaw.NStandardPid(h, 0.1254, 11.3257, 1.9056, 2.7963e3);
	c_yaw.Clamping(-1.0,1.0);
	c_yaw.SteadyStateInit(0);

	// main loop
	std::cout << "attitude controller started" << std::endl;
	float e = 0;
	while(ros::ok()){
		e = 0 - roll;
		c_msg.y = c_roll.Update(e);
        e = 0 - pitch;
        c_msg.x = c_pitch.Update(e);
        e = 0 - yaw;
        c_msg.z = c_yaw.Update(e);
		ctt_pub.publish(c_msg);
		ros::spinOnce();
		r.sleep();
	}
	return 0;
}
