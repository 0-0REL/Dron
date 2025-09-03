/**
 * @file    act_mot.cpp
 * @brief   Activa motores.
 * @author  Rodrigo
 * @date    12-Jul-2024
 * @version 1.0
 *
 * @details
 * - Recibe mensajes del control de actidud.
 * - Se limita señal a [1000, 2000].
 * - Nodo: act_mot
 * - Suscrito: motors
 */

//ros
#include "ros/ros.h"
#include "std_msgs/Float32MultiArray.h"
//navio drivers
#include <unistd.h>
#include "Navio2/PWM.h"
#include "Navio2/RCOutput_Navio2.h"
#include "Common/Util.h"
#include <unistd.h>
#include <memory>

//salida de los motores
int mot[4] = {1000,1000,1000,1000};
//RCOutput_Navio2 pwm;

void att_ctrlCallback(const std_msgs::Float32MultiArray::ConstPtr& msg);

int main(int argc, char **argv){
   ros::init(argc, argv, "act_mot");
   ros::NodeHandle nh_mot;
   ros::Subscriber mot_sub = nh_mot.subscribe("motors", 1, att_ctrlCallback); //suscrito a att_ctrl
   //motores de 1 a 4
   RCOutput_Navio2 pwm;
   for(int idx = 0; idx < 4; idx ++){
      pwm.initialize(idx);
      pwm.set_frequency(idx,250);
      pwm.enable(idx);
      usleep(200000); // 200 ms de delay
   }
   for (int i = 0; i<10; i++){
       for(int idx = 0; idx<4; idx++) pwm.set_duty_cycle(idx,1000);
       usleep(200000);
   }

   while(ros::ok()){
      for(int idx = 0; idx<4; idx++) pwm.set_duty_cycle(idx,mot[idx]);
      ROS_INFO("Mot_PWM: %d %d %d %d", mot[0], mot[1], mot[2], mot[3]);
      ros::spinOnce();
   }
   //ros::spin();
   return 0;
}

void att_ctrlCallback(const std_msgs::Float32MultiArray::ConstPtr& msg)
{
   for (size_t i = 0; i < msg->data.size(); ++i){
      mot[i] = msg->data[i];
      mot[i] = (int)((mot[i]<1000)? 1000 : (mot[i]>2000)? 2000 : mot[i]);
      //pwm.set_duty_cycle(i, mot[i]);
   }
   //ROS_INFO("Mot_PWM: %d %d %d %d", mot[0], mot[1], mot[2], mot[3]);
}
