//ros
#include "ros/ros.h"
#include "geometry_msgs/Vector3.h"
//navio
#include <unistd.h>
#include <string>
#include <memory>
#include <cmath>
#include <Common/MPU9250.h>
#include <Common/Util.h>
#include <MadgwickAHRS/MadgwickAHRS.h>

#define sampleFreq 250.0f

void getEuler(float* roll, float* pitch, float* yaw)
{
   *roll = atan2f(q0*q1+q2*q3, 0.5f-q1*q1-q2*q2);
   *pitch = asinf(2.0f*(q0*q2-q3*q1));
   *yaw = atan2f(q0*q3+q1*q2, 0.5f-q2*q2-q3*q3);
}

int main(int argc, char **argv)
{
    ros::init(argc,argv,"imu_mpu");
    ros::NodeHandle nh_mpu;
    ros::Publisher mpu_pub = nh_mpu.advertise<geometry_msgs::Vector3>("ahrs_mpu",1000);
    ros::Rate r_mpu((int)sampleFreq); //100 Hz
    geometry_msgs::Vector3 msg;
//    beta = 0.5f;
    if (check_apm()) {
        return 1;
    }

    MPU9250 mpu;

    if (!mpu.probe()) {
        printf("Sensor not enabled\n");
        return EXIT_FAILURE;
    }
    mpu.initialize();

    float ax, ay, az;
    float gx, gy, gz;
    float mx, my, mz;

    float roll, pitch, yaw;
//-------------------------------------------------------------------------
    while(ros::ok()) {
//sensores
        mpu.update();
        mpu.read_accelerometer(&ax, &ay, &az);
        mpu.read_gyroscope(&gx, &gy, &gz);
        mpu.read_magnetometer(&mx, &my, &mz);
//ahrs
        MadgwickAHRSupdate(gx,gy,gz,ax,ay,az,mx,my,mz);
        getEuler(&roll, &pitch, &yaw);
	msg.x = roll;
	msg.y = pitch;
	msg.z = yaw;
	// se envia mensaje
	ROS_INFO("Orientacion: x = %.2f, y = %.2f, z = %.2f", msg.x*57.295f, msg.y*57.259f, msg.z*57.295f);
	mpu_pub.publish(msg);
	ros::spinOnce();
        r_mpu.sleep();
    }
}
