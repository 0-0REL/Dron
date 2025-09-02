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
#include "std_msgs/Float32.h"
//navio
#include <Common/MS5611.h>
#include <Common/Util.h>
#include <unistd.h>
#include <stdio.h>

int main(int argc, char **argv)
{
    ros::init(argc,argv,"barometro");
    ros::NodeHandle nh_baro;
    ros::Publisher baro_pub = nh_baro.advertise<std_msgs::Float32>("alt_est",2);
    ros::Rate rate(100);
    std_msgs::Float32 H_b;
    MS5611 barometer;

    if (check_apm()) {
        return 1;
    }

    barometer.initialize();

	float R = 287.1;        // J/kgK
	float k_T = 6.5e-3;     // K/m
	float g_0 = 9.80665;    // m/s^2
	barometer.update();
	float T_s = barometer.getTemperature();
	float p_s = barometer.getPressure();
    while (ros::ok()) {
        barometer.update();
		float p_b = barometer.getPressure();
		H_b.data = (T_s/k_T)*(pow((p_b/p_s),-(R*k_T/g_0))-1);
        ROS_INFO("Altura: %.3f m", H_b.data);
        baro_pub.publish(H_b);
        ros::spinOnce();
        rate.sleep();
    }
    return 0;
}

