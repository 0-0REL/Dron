cmake_minimum_required(VERSION 3.10)
project(navio_imu)

set(CMAKE_CXX_STANDARD 11)

# Incluye los directorios de encabezados
include_directories(
    ${CMAKE_SOURCE_DIR}/Common
    ${CMAKE_SOURCE_DIR}/Navio2
    ${CMAKE_SOURCE_DIR}/MadgwickAHRS
)

# Archivos fuente
set(SOURCES
    imu.cpp
    Common/MPU9250.cpp
    Common/Util.cpp
    Common/SPIdev.cpp      # <-- Agrega esta línea
    Navio2/LSM9DS1.cpp
    MadgwickAHRS/MadgwickAHRS.c
)

add_executable(imu ${SOURCES})

# Librerías del sistema necesarias
target_link_libraries(imu m pthread)