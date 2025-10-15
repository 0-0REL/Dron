/**
 * @file    imu_mpu.cpp
 * @brief   AHRS using MPU9250.
 * @author  @0-0REL
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
#include <sys/socket.h>  // Para funciones de socket
#include <netinet/in.h>  // Para sockaddr_in
#include <arpa/inet.h>   // Para inet_addr()
#include <cstring>       // Para memcpy()
#include <iostream>      // Para std::cerr
extern "C"{
    //#include <MadgwickAHRS/MadgwickAHRS.h>
    #include <AHRS/MahonyAHRS.h>
}
// HAT
#include <Common/MPU9250.h>
#include <Common/Util.h>

#define sampleFreq 510.0f

// Convert quaternion to Euler angles
void getEuler(float* roll, float* pitch, float* yaw);

class Socket {
public:
    // Constructor con IP y puerto por defecto (tu configuración)
   Socket(const char* ip = "100.88.148.66", int port = 7000) {
        sockfd = socket(AF_INET, SOCK_DGRAM, 0);
        if (sockfd < 0) {
            std::cerr << "Error al crear el socket" << std::endl;
            exit(EXIT_FAILURE);
        }

        servaddr.sin_family = AF_INET;
        servaddr.sin_port = htons(port);
        servaddr.sin_addr.s_addr = inet_addr(ip);
    }

    // Función que acepta 4 floats y los envía
    void sendFloats(float w, float x, float y, float z) {
        char buffer[sizeof(float) * 4];  // Buffer para 4 floats
        memcpy(buffer, &w, sizeof(float));
        memcpy(buffer + sizeof(float), &x, sizeof(float));
        memcpy(buffer + 2 * sizeof(float), &y, sizeof(float));
        memcpy(buffer + 3 * sizeof(float), &z, sizeof(float));

        sendto(
            sockfd, buffer, sizeof(buffer), 0,
            (struct sockaddr*)&servaddr, sizeof(servaddr)
        );
    }

    ~Socket() {
        close(sockfd);  // Cierra el socket al destruir el objeto
    }

private:
    int sockfd;
    struct sockaddr_in servaddr;
};

int main(int argc, char **argv)
{
    ros::init(argc,argv,"imu_mpu");
    ros::NodeHandle nh_mpu;
    ros::Publisher mpu_pub = nh_mpu.advertise<geometry_msgs::Vector3>("ahrs_mpu",1000);
    //ros::Publisher mpu_q = nh_mpu.advertise<std_msgs::Float32MultiArray>("ahrs_q_mpu", 1000);
    ros::Rate r_mpu((int)sampleFreq);
    geometry_msgs::Vector3 msg;
    //std_msgs::Float32MultiArray qmsg;
    // ganacias de filtros
    beta = 0.041f;
    //twoKp = 2;
    //twoKi = 0.6;
    //

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

    Socket sock;  // Usa IP y puerto por defecto
//-------------------------------------------------------------------------
    while(ros::ok())
    {
        //sensores
        mpu.update();
        mpu.read_accelerometer(&ax, &ay, &az);
        mpu.read_gyroscope(&gx, &gy, &gz);
        mpu.read_magnetometer(&mx, &my, &mz);

        //ahrs
        gx -= gyroCal[0];
        gy -= gyroCal[1];
        gz -= gyroCal[2];
        //MahonyAHRSupdateIMU(gx,gy,gz,ax,ay,az);
	MahonyAHRSupdate(gx,gy,gz,ax,ay,az,mx,my,mz);
        getEuler(&roll, &pitch, &yaw);
        msg.x = roll; //pitch
        msg.y = pitch; //roll
        msg.z = yaw;

	sock.sendFloats(q0, q1, q2, q3);  // Envía los 4 floats
        // se envia mensaje
        ROS_INFO("Orientacion: roll = %.2f, pitch = %.2f, yaw = %.2f", msg.y, msg.x, msg.z);
        mpu_pub.publish(msg);
	//qmsg.data = {q0, q1, q2, q3};
	//mpu_q.publish(qmsg);
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
