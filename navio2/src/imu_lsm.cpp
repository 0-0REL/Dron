//ros
#include "ros/ros.h"
#include "geometry_msgs/Vector3.h"
//navio
#include <unistd.h>
#include <string>
#include <memory>
#include <cmath>
#include <Navio2/LSM9DS1.h>
#include <Common/Util.h>
#include <MadgwickAHRS/MadgwickAHRS.h>

#define sampleFreq 250.0f

void getEuler(float* roll, float* pitch, float* yaw)
{
   *roll = atan2(2*(q0*q1+q2*q3), 1-2*(q1*q1+q2*q2)) * 180.0/M_PI;
   *pitch = asin(2*(q0*q2-q3*q1)) * 180.0/M_PI;
   *yaw = atan2(2*(q0*q3+q1*q2), 1-2*(q2*q2+q3*q3)) * 180.0/M_PI;
}

int main(int argc, char **argv)
{
    ros::init(argc,argv,"imu_lsm");
    ros::NodeHandle nh_mpu;
    ros::Publisher mpu_pub = nh_mpu.advertise<geometry_msgs::Vector3>("ahrs_lsm",1000);
    ros::Rate r_mpu((int)sampleFreq); //512 Hz
    geometry_msgs::Vector3 msg;

    LSM9DS1 lsm;
    if (check_apm()) {
        return 1;
    }

    if (!lsm.probe()) {
        printf("Sensor not enabled\n");
        return EXIT_FAILURE;
    }
    lsm.initialize();

    float ax, ay, az;
    float gx, gy, gz;
    float mx, my, mz;

    float roll, pitch, yaw;
//-------------------------------------------------------------------------
    while(ros::ok()) {
//sensores
        lsm.update();
        lsm.read_accelerometer(&ax, &ay, &az);
        lsm.read_gyroscope(&gx, &gy, &gz);
        lsm.read_magnetometer(&mx, &my, &mz);
//ahrs
        MadgwickAHRSupdate(gx,gy,gz,ax,ay,az,mx,my,mz);
        getEuler(&roll, &pitch, &yaw);
	msg.x = roll;
	msg.y = pitch;
	msg.z = yaw;
	// se envia mensaje
	ROS_INFO("Orientacion: x = %.2f, y = %.2f, z = %.2f", msg.x, msg.y, msg.z);
	mpu_pub.publish(msg);
	ros::spinOnce();
        r_mpu.sleep();
    }
}
