// ROS
#include "ros/ros.h"
#include "geometry_msgs/Vector3.h"
#include "std_msgs/Float32.h"
//
#include "iostream"
#include "sys_ctrl/cmon-pid.h"

float pitch = 0;

void MPUahrsCallback(const geometry_msgs::Vector3::ConstPtr& msg){
        pitch = msg->x;
}

int main(int argc, char **argv){
        // Initialize ROS
        ros::init(argc, argv, "pthCtrl");
        ros::NodeHandle nh;
        ros::Publisher ctt_pub = nh.advertise<std_msgs::Float32>("pt_PID",1);
        ros::Subscriber mpu_sub = nh.subscribe("ahrs_mpu", 1, MPUahrsCallback);
        ros::Rate lr(250);
        // message setup
        std_msgs::Float32 p_msg;
        // PID setup
        clamping_t<pid_bwe> pid;
        constexpr double sampling_time = 1/250;
        constexpr double kp = 0.212170;
        constexpr double ki = 0;
        constexpr double kd = 0.078595;
        constexpr double tf = sampling_time/2;
        pid.Clamping(-3,3);
        pid.ParallelPid(sampling_time,kp,ki,kd,tf);
        pid.SteadyStateInit(0);
        // main loop
        std::cout << "pitch control started" << std::endl;
        while(ros::ok()){
                double e = 0 - pitch;
                double u = pid.Update(e);
                p_msg.data = u;
                ctt_pub.publish(p_msg);
                ros::spinOnce();
                lr.sleep();
        }
        return 0;
}
