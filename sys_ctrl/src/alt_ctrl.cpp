/**
 * @file alt_ctrl.cpp
 * @author @0-0REL
 * @brief Altitude controller node
 * @version 1.0
 * @date 09-10-2025
 * @details This node control the thrust needed to maintain altitude
 */
// ROS
#include "ros/ros.h"
#include "std_msgs/Float32.h"
// C++
#include "sys_ctrl/cmon-pid.h"

int main(int argc, char **argv){
    // Initialize ROS
    ros::init(argc, argv, "alt_ctrl");
    ros::NodeHandle nh;
	ros::Publisher pub = nh.advertise<std_msgs::Float32MultiArray>("thrust",1);
    ros::Rate rate(250);
    // PID setup
    /*clamping_t<pid_bwe> pid;
    constexpr double sampling_time = 1.0/250.0;
    constexpr double kp = 0.212170;
    constexpr double ki = 0.0;
    constexpr double kd = 0.078595;
    constexpr double tf = sampling_time/2.0;
    pid.Clamping(-0.4,0.4);
    pid.NStandardPid();
    pid.SteadyStateInit(0);*/
    // message setup
    std_msgs::Float32MultiArray msg_thrust;
    int i = 0;
    float thrust = 0;
    while(ros::ok()){
        thrust = i*0.7/750.0*9.81;
        msg_thrust.data = thrust;
        pub.publish(msg_thrust);
        ros::spinOnce();
        if (i >= 750) i = 750;
        else thrust++;
        rate.sleep();
    }
    return 0;
}