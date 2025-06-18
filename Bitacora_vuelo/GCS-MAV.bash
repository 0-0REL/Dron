#!/bin/bash

#mavproxy.py --master=/dev/ttyUSB0,57600 --out 127.0.0.1:14550 --console --aircraft=Dron
mavproxy.py --master=192.168.68.103:14650 --out 127.0.0.1:14550 --console --aircraft=Dron
