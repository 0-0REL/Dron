/**
 * @file    imu_lsm.cpp
 * @brief   AHRS using LSM9DS1.
 * @author  Rodrigo
 * @date    12-Jul-2025
 * @version 1.0
 *
 * @details Mahony filter.
 */
// ROS
#include "ros/ros.h"
#include "geometry_msgs/Vector3.h"
//#include "std_msgs/Float32MultiArray.h"
// C++
#include <unistd.h>
#include <string>
#include <memory>
#include <cmath>
extern "C" {
    //#include <MadgwickAHRS/MadgwickAHRS.h>
    #include <AHRS/MahonyAHRS.h>
}
// HAT
#include <Navio2/LSM9DS1.h>
#include <Common/Util.h>

#define sampleFreq 510.0f

// Convert quaternion to Euler angles
void getEuler(float* roll, float* pitch, float* yaw);

int main(int argc, char **argv)
{
    ros::init(argc,argv,"imu_lsm");
    ros::NodeHandle nh_mpu;
    ros::Publisher mpu_pub = nh_mpu.advertise<geometry_msgs::Vector3>("ahrs_lsm",1000);
    //ros::Publisher lsm_q = nh_mpu.advertise<std_msgs::Float32MultiArray>("ahrs_q_lsm", 1000);
    ros::Rate r_mpu((int)sampleFreq);
    geometry_msgs::Vector3 msg;
    //std_msgs::Float32MultiArray qmsg;
    // Gancias de los filtros
    //beta = 2;
    twoKp = 2;
    twoKi = 0.5;

    LSM9DS1 lsm;

    if (!lsm.probe()) {
        printf("Sensor not enabled\n");
        return EXIT_FAILURE;
    }
//------------------------------------------------------------------------
    lsm.initialize();
    float ax, ay, az;
    float gx, gy, gz;
    float mx, my, mz;
    float roll, pitch, yaw;
    float gyroCal[3] = {0.0, 0.0, 0.0};
    //calibracion
    printf("calibrando...\n");
    for(int i = 0; i<100; i++){
	lsm.update();
	lsm.read_gyroscope(&gx,&gy,&gz);
	gyroCal[0] += gx;
	gyroCal[1] += gy;
	gyroCal[2] += gz;
	usleep(10000);
    }
    gyroCal[0] /= 100;
    gyroCal[1] /= 100;
    gyroCal[2] /= 100;
    printf("GyroOffset: %f %f %f", gyroCal[0], gyroCal[1], gyroCal[2]);
//-------------------------------------------------------------------------
    while(ros::ok()) {
        //sensores
        lsm.update();
        lsm.read_accelerometer(&ax, &ay, &az);
        lsm.read_gyroscope(&gx, &gy, &gz);
        //lsm.read_magnetometer(&mx, &my, &mz);

        //ahrs
        gx -= gyroCal[0];
        gy -= gyroCal[1];
        gz -= gyroCal[2];
        //MadgwickAHRSupdate(gx,gy,gz,ax,ay,az,mx,my,mz);
        MahonyAHRSupdateIMU(gx, gy, gz, ax, ay, az);
        getEuler(&roll, &pitch, &yaw);
        msg.x = roll; //pitch
        msg.y = pitch; //roll
        msg.z = yaw;

        // se envia mensaje
        ROS_INFO("Orientacion: roll = %.2f, pitch = %.2f, yaw = %.2f", msg.y*57.2957795, msg.x*57.2957795, msg.z*57.2957795);
        mpu_pub.publish(msg);
	//qmsg.data = {q0, q1, q2, q3};
	//lsm_q.publish(qmsg);
        ros::spinOnce();
        r_mpu.sleep();
    }
    return 0;
}

void getEuler(float* roll, float* pitch, float* yaw)
{
  //*yaw = atan2(2.0f*q1*q2 - 2.0f*q0*q3, 2.0f*q0*q0 + 2.0f*q1*q1 - 1.0f);
  //*pitch = -asin(2.0f*q1*q3 + 2.0f*q0*q2);
  //*roll = atan2(2.0f*q2*q3 - 2.0f*q0*q1, 2.0f*q0*q0 + 2.0f*q3*q3 - 1.0f);

  *roll = atan2(2*(q0*q1+q2*q3), 1-2*(q1*q1+q2*q2));
  *pitch = asin(2*(q0*q2-q3*q1));
  *yaw = atan2(2*(q0*q3+q1*q2), 1-2*(q2*q2+q3*q3));
}
