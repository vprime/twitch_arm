#!/usr/bin/python

import serial
import time

ser = serial.Serial('/dev/ttyUSB1')
print(ser.name)
ser.write(b'b-100;')
time.sleep(3)
ser.write(b'b0;')
ser.close()
