/**
 * @file    imu_mpu.cpp
 * @brief   AHRS con IMU MPU9250.
 * @author  Rodrigo
 * @date    12-Jul-2024
 * @version 1.0
 *
 * @details
 * - Filtro Mahony para AHRS.
 * - Nodo: imu_mpu
 * - Publica: ahrs_mpu
 * - Frecuencia: 510 Hz
 */

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

extern "C"{
    //#include <MadgwickAHRS/MadgwickAHRS.h>
    #include <MahonyAHRS/MahonyAHRS.h>
}

#define sampleFreq 510.0f

// Convert quaternion to Euler angles
void getEuler(float* roll, float* pitch, float* yaw);

int main(int argc, char **argv)
{
    ros::init(argc,argv,"imu_mpu");
    ros::NodeHandle nh_mpu;
    ros::Publisher mpu_pub = nh_mpu.advertise<geometry_msgs::Vector3>("ahrs_mpu",1000);
    ros::Publisher mpu_q = nh_mpu.advertise<
    ros::Rate r_mpu((int)sampleFreq);
    geometry_msgs::Vector3 msg;
    // ganacias de filtros
//  beta = 0.5f;
    twoKp = 8.0;
    twoKi = 0.5;
    //
    if (check_apm()) {
        return 1;
    }

    MPU9250 mpu;

    if (!mpu.probe()) {
        printf("Sensor not enabled\n");
        return EXIT_FAILURE;
    }
    mpu.initialize();
//------------------------------------------------------------------------
    float ax, ay, az;
    float gx, gy, gz;
    float mx, my, mz;
    float roll, pitch, yaw;
    float gyroCal[3] = {0.0, 0.0, 0.0};
//calibracion
    printf("calibrando...\n");
    for(int i = 0; i<100; i++){
	mpu.update();
	mpu.read_gyroscope(&gx,&gy,&gz);
	gyroCal[0] += gx;
	gyroCal[1] += gy;
	gyroCal[2] += gz;
	usleep(10000);
    }
    gyroCal[0] /= 100;
    gyroCal[1] /= 100;
    gyroCal[2] /= 100;
    printf("offset gyro %f %f %f\n", gyroCal[0], gyroCal[1], gyroCal[2]);
//-------------------------------------------------------------------------
    while(ros::ok())
    {
        //sensores
        mpu.update();
        mpu.read_accelerometer(&ax, &ay, &az);
        mpu.read_gyroscope(&gx, &gy, &gz);
        //mpu.read_magnetometer(&mx, &my, &mz);

        //ahrs
        gx -= gyroCal[0];
        gy -= gyroCal[1];
        gz -= gyroCal[2];
        //MadgwickAHRSupdate(gx,gy,gz,ax,ay,az,mx,my,mz);
        MahonyAHRSupdateIMU(gx,gy,gz,ax,ay,az);
        getEuler(&roll, &pitch, &yaw);
        msg.x = roll;
        msg.y = pitch;
        msg.z = yaw;
        // se envia mensaje
        ROS_INFO("Orientacion: roll = %.2f, pitch = %.2f, yaw = %.2f", msg.x*57.2957795, msg.y*57.2957795, msg.z*57.2957795);
        mpu_pub.publish(msg);
        ros::spinOnce();
        r_mpu.sleep();
    }
    return 0;
}

void getEuler(float* roll, float* pitch, float* yaw)
{
  *yaw = atan2(2.0f*q1*q2 - 2.0f*q0*q3, 2.0f*q0*q0 + 2.0f*q1*q1 - 1.0f);
  *pitch = -asin(2.0f*q1*q3 + 2.0f*q0*q2);
  *roll = atan2(2.0f*q2*q3 - 2.0f*q0*q1, 2.0f*q0*q0 + 2.0f*q3*q3 - 1.0f);
}
