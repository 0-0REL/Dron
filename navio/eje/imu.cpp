#include <unistd.h>
#include <string>
#include <memory>
#include <cmath>
#include "Common/MPU9250.h"
#include "Navio2/LSM9DS1.h"
#include "Common/Util.h"
extern "C"{
#include "MadgwickAHRS/MadgwickAHRS.h"
}
//#define G_SI 9.80665
//#define PI   3.14159

void getEuler(float* roll, float* pitch, float* yaw)
{
   *roll = atan2(2*(q0*q1+q2*q3), 1-2*(q1*q1+q2*q2)) * 180.0/M_PI;
   *pitch = asin(2*(q0*q2-q3*q1)) * 180.0/M_PI;
   *yaw = atan2(2*(q0*q3+q1*q2), 1-2*(q2*q2+q3*q3)) * 180.0/M_PI;
}

int main(int argc, char *argv[])
{

    if (check_apm()) {
        return 1;
    }

    auto sensor = std::unique_ptr <InertialSensor>{ new MPU9250() };

    if (!sensor->probe()) {
        printf("Sensor not enabled\n");
        return EXIT_FAILURE;
    }
    sensor->initialize();

    float ax, ay, az;
    float gx, gy, gz;
    float mx, my, mz;

    float roll, pitch, yaw;
//-------------------------------------------------------------------------

    while(1) {
        sensor->update();
        sensor->read_accelerometer(&ax, &ay, &az);
        sensor->read_gyroscope(&gx, &gy, &gz);
        sensor->read_magnetometer(&mx, &my, &mz);
        /*printf("Acc: %+7.3f %+7.3f %+7.3f  ", ax, ay, az);
        printf("Gyr: %+8.3f %+8.3f %+8.3f  ", gx, gy, gz);
        printf("Mag: %+7.3f %+7.3f %+7.3f\n", mx, my, mz);*/
        MadgwickAHRSupdate(gx,gy,gz,ax,ay,az,mx,my,mz);
        getEuler(&roll, &pitch, &yaw);
        printf("ROLL: %+05.2f PITCH: %+05.2f YAW: %+05.2f\n", roll, pitch, yaw);
        usleep(500000);
    }
}
