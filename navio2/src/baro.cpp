/**
 * @file    baro.cpp
 * @brief   Barometro para esimar altura.
 * @author  Rodrigo
 * @date    12-Jul-2024
 * @version 1.0
 * 
 * @details
 * - Estima altura.
 * - Nodo: barometro.
 * - Publica: alt_est.
 */

//ros
#include "ros/ros.h"
#include "std_msgs/Float32MultiArray.h"
//navio
#include <Common/MS5611.h>
#include <Common/Util.h>
#include <unistd.h>
#include <stdio.h>

int main(int argc, char **argv)
{
    ros::init(argc,argv,"barometro");
    ros::NodeHandle nh_baro;
    ros::Publisher baro_pub = nh_baro.advertise<std_msgs::Float32MultiArray>("alt_est",10);
   // ros::Rate rt_br(5);
    std_msgs::Float32MultiArray msg;
    msg.data.resize(2);
    MS5611 barometer;

    if (check_apm()) {
        return 1;
    }

    barometer.initialize();

    while (ros::ok()) {
        barometer.refreshPressure();
        usleep(10000); // Waiting for pressure data ready
        barometer.readPressure();
	    msg.data[0] = barometer.getPressure();

        barometer.refreshTemperature();
        usleep(10000); // Waiting for temperature data ready
        barometer.readTemperature();
        msg.data[1] = barometer.getTemperature();

        barometer.calculatePressureAndTemperature();

        ROS_INFO("Temperatura: %.2f \tPresion: %.2f", msg.data[0], msg.data[1]);
        baro_pub.publish(msg);
        ros::spinOnce();
        //rt_br.sleep();
    }
    return 0;
}

