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
extern "C" {
    //#include <MadgwickAHRS/MadgwickAHRS.h>
    #include <MahonyAHRS/MahonyAHRS.h>
}

#define sampleFreq 510.0f

void getEuler(float* roll, float* pitch, float* yaw)
{
    *yaw = atan2(2.0f*q1*q2 - 2.0f*q0*q3, 2.0f*q0*q0 + 2.0f*q1*q1 - 1.0f);
    *pitch = -asin(2.0f*q1*q3 + 2.0f*q0*q2);
    *roll = atan2(2.0f*q2*q3 - 2.0f*q0*q1, 2.0f*q0*q0 + 2.0f*q3*q3 - 1.0f);
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
//------------------------------------------------------------------------
    lsm.initialize();
    float ax, ay, az;
    float gx, gy, gz;
    float mx, my, mz;
    float roll, pitch, yaw;
    float gyroCal[3] = {0.0, 0.0, 0.0};
    
    //calibracion
    printf("calibrando...\n");
    for(int i = 0; i<100; i++);
    {
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
