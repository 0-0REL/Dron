// ROS
#include "ros/ros.h"
#include "geometry_msgs/Vector3.h"
#include "std_msgs/Float32MultiArray.h"
//
#include "iostream"
#include "sys_ctrl/AutoTunePID.h"

float roll = 0, pitch = 0, yaw = 0;

void MPUahrsCallback(const geometry_msgs::Vector3::ConstPtr& msg){
	roll = msg->y;
	pitch = msg->x;
	yaw = msg->z;
}

int main(int argc, char **argv){
	ros::init(argc, argv, "stblz");
	ros::NodeHandle nh;
	ros::Publisher ctt_pub = nh.advertise<std_msgs::Float32MultiArray>("motor",1);
	ros::Subscriber mpu_sub = nh.subscribe("ahrs_mpu", 1, MPUahrsCallback);
	ros::Rate lr(250);

	std_msgs::Float32MultiArray mot_msg;
	mot_msg.layout.dim.push_back(std_msgs::MultiArrayDimension());
	mot_msg.layout.dim[0].label = "motors";
	mot_msg.layout.dim[0].size = 4;
	mot_msg.layout.dim[0].stride = 4;

	float spr = 0.0f, spp = 0.0f, spy = 0.0;
	AutoTunePID pid(-255,255,TuningMethod::ZieglerNichols);
	// Configure PID controller
	pid.setSetpoint(spr); // Set the desired setpoint
	pid.setOscillationMode(OscillationMode::Half); // Set oscillation mode to Half (default steps = 20)
	pid.setOperationalMode(OperationalMode::Tune); // Start in Tune mode for auto-tuning

	std::cout << "Control de actitud iniciado" << std::endl;
	while(ros::ok()){
		pid.update(roll);
		float r_out = pid.getOutput();

		mot_msg.data.clear();  // Importante: limpiar datos anteriores
		mot_msg.data = {1100.0, 1100.0, 1100.0, 1100.0};
		ctt_pub.publish(mot_msg);
		ros::spinOnce();
		lr.sleep();
	}
	mot_msg.data.clear();  // Importante: limpiar datos anteriores
	mot_msg.data = {1000.0, 1000.0, 1000.0, 1000.0};
	ctt_pub.publish(mot_msg);
	ROS_DEBUG("Programa finalizado\nKp: %f\tKi: %f\tKd: %f",pid.getKp(), pid.getKi(), pid.getKd());
	return 0;
}
