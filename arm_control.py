#!/usr/bin/python
""" 
Self Protecting OWI/Maplin USB Arm control
-----
Allows you to have a basic feedback loop using a microphone attached to the arm.
Listens for gearbox clicking, and halts movement to prevent damage.

Based on the robotic_arm_driver example here: 
https://github.com/maxinbjohn/robotic_arm_driver/blob/master/examples/python/motor.py

MIT License

Copyright (c) 2017 Vincent Prime

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import fnmatch
import sys
import time

import audioop
import pyaudio

halted = {
	"1":[],
	"2":[]
}

inputDevice = 0
threshold = 2000



""" Locate the sysfs entry corresponding to USB Robotic ARM """
def find_usb_device():
	for file in os.listdir('/sys/bus/usb/drivers/robotic_arm/'):
                if fnmatch.fnmatch(file, '*:*'):
                        return file


def runTilTimeOrNoise(time, motor, action):
    chunk = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    
    p = pyaudio.PyAudio()
    
    stream = p.open(format=FORMAT,
                channels=CHANNELS, 
                rate=RATE, 
                input=True,
                output=True,
                input_device_index=inputDevice,
                frames_per_buffer=chunk)
    end = time.time() + time

	fd= open(motor, "w")
	fd.write(action)
	fd.close()

    while time.time() < end:
        data = stream.read(chunk)
        # check level against threshold, you'll have to write getLevel()
        rms = audioop.rms(data, 2)  #width=2 for format=paInt16
        if rms > threshold:
        	halted[action].append(motor)
            break
    stop(motor)
    stream.stop_stream()
    stream.close()
    p.terminate()


""" To roate the motor in clockwise direction """
def move_clockwise(motor, time):
	# Check for halt, and disallow running
	if motor in halted["1"]:
		print "Unable to comply, motor at limit."
		return
	runTilTimeOrNoise(time, motor, "1")
	# Clear opposing halt
	if motor in halted["2"]: halted["2"].remove(motor)


""" To roate the motor in anti-clockwise direction """
def move_anti_clockwise(motor, time):
	# Check for halt, and disallow running
	if motor in halted["2"]:
		print "Unable to comply, motor at limit."
		return
	runTilTimeOrNoise(time, motor, "2")
	# Clear opposing halt
	if motor in halted["1"]: halted["1"].remove(motor)


""" To stop the current activity """
def stop(device):
	fd= open(device, "w")
	fd.write("0")
	fd.close()
	
""" To switch on LED in Robotic ARM """
def led_on(led):
	fd= open(led, "w")
	fd.write("1")
	fd.close()

if __name__ == '__main__':

	usb_dev_name = find_usb_device()
	
	if ( usb_dev_name == None):
		print "Please ensure that robotic_arm module is loaded "
		print " Also ensure that you have connected the robotic arm "
		print " and switched on the Robotic ARM device"
                sys.exit(-1)

	# Path for the robotic arm sysfs entries
	robotic_arm_path= "/sys/bus/usb/drivers/robotic_arm/"+ usb_dev_name + "/"

	# Switch on and off the LED in Robotic arm
	print "LED control"
	led= robotic_arm_path+"led"
	led_on(led)
	time.sleep(1)
	stop(led)

	# Move the base 
	print "Base Motor control"
	base= robotic_arm_path+"basemotor"
	move_clockwise(base, 2)
	move_anti_clockwise(base, 2)
	stop(base)
		
	# Move the base 
	print "Grip control"
	grip= robotic_arm_path+"gripmotor"
	move_clockwise(grip, 1)
	move_anti_clockwise(grip, 1)
	stop(grip)

	# Move the Wrist
	print "Wrist Motor control"
	wrist= robotic_arm_path+"motor2"
	move_clockwise(wrist, 1)
	move_anti_clockwise(wrist, 1)
	stop(wrist)

	# Move the Elbow
	print "Elbow Motor control"
	elbow= robotic_arm_path+"motor3"
	move_clockwise(elbow, 1)
	move_anti_clockwise(elbow, 1)
	stop(elbow)

	# Move the Shoulder
	print "Shoulder Motor control"
	shoulder= robotic_arm_path+"motor4"
	move_clockwise(shoulder, 1)
	move_anti_clockwise(shoulder, 1)
	stop(shoulder)