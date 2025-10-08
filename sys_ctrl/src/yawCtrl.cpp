// ROS
#include "ros/ros.h"
#include "geometry_msgs/Vector3.h"
#include "std_msgs/Float32.h"
//
#include "iostream"
#include "sys_ctrl/cmon-pid.h"

float yaw = 0;

void MPUahrsCallback(const geometry_msgs::Vector3::ConstPtr& msg){
	yaw = msg->z;
}

int main(int argc, char **argv){
	// Initialize ROS
	ros::init(argc, argv, "yawCtrl");
	ros::NodeHandle nh;
	ros::Publisher ctt_pub = nh.advertise<std_msgs::Float32>("yw_PID",1);
	ros::Subscriber mpu_sub = nh.subscribe("ahrs_mpu", 1, MPUahrsCallback);
	ros::Rate lr(250);
	// message setup
	std_msgs::Float32 y_msg;
	// PID setup
	clamping_t<pid_bwe> pid;
	constexpr double sampling_time = 1/250;
	constexpr double kp = 0.401057;
	constexpr double ki = 0;
	constexpr double kd = 0.148564;
	constexpr double tf = sampling_time/2;
	pid.Clamping(-3,3);
	pid.ParallelPid(sampling_time,kp,ki,kd,tf);
	pid.SteadyStateInit(0);
	// main loop
	std::cout << "yaw control started" << std::endl;
	while(ros::ok()){
		double e = 0 - roll;
		double u = pid.Update(e);
		y_msg.data = u;
		ctt_pub.publish(y_msg);
		ros::spinOnce();
		lr.sleep();
	}
	return 0;
}
