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

import thread

class Arm:
    halted = {
        "1":[],
        "2":[]
    }
    running = []

    inputDevice = 0
    threshold = 2000
    chunk = 1024
    listening = True

    """ Locate the sysfs entry corresponding to USB Robotic ARM """
    def find_usb_device(self):
        for file in os.listdir('/sys/bus/usb/drivers/robotic_arm/'):
                    if fnmatch.fnmatch(file, '*:*'):
                            return file

    def setupAudioStream(self):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 8000
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                    channels=CHANNELS, 
                    rate=RATE, 
                    input=True,
                    output=True,
                    frames_per_buffer=self.chunk)
        self.listening = True
        while self.listening:
            data = stream.read(self.chunk, exception_on_overflow = False)
            rms = audioop.rms(data, 2)  #width=2 for format=paInt16
            print("RMS: " + str(rms))
            if rms > self.threshold:
                self.stopRunningMotors()
        stream.stop_stream()
        stream.close()
        p.terminate()

    def stopRunningMotors(self):
        for motor in self.running:
            self.halted[motor[1]].append(motor[0])
            self.stop(motor[0])

    """ Run the motor till it makes a noise"""
    def runTilTime(self, sec, motor, action):
        fd = open(motor, "w")
        fd.write(action)
        fd.close()
        time.sleep(sec)
        self.stop(motor)

    """ To roate the motor in clockwise direction """
    def move_clockwise(self, motor, sec):
        # Check for halt, and disallow running
        if motor in self.halted["1"]:
            print "Unable to comply, motor at limit."
            return
        self.running.append([motor, "1"])
        self.runTilTime(sec, motor, "1")
        # Clear opposing halt
        if motor in self.halted["2"]: self.halted["2"].remove(motor)


    """ To roate the motor in anti-clockwise direction """
    def move_anti_clockwise(self, motor, sec):
        # Check for halt, and disallow running
        if motor in self.halted["2"]:
            print "Unable to comply, motor at limit."
            return
        self.running.append([motor, "2"])
        self.runTilTime(sec, motor, "2")
        # Clear opposing halt
        if motor in self.halted["1"]: self.halted["1"].remove(motor)


    """ To stop the current activity """
    def stop(self, device):
        fd= open(device, "w")
        fd.write("0")
        fd.close()
        for key, value in self.running:
            if value[0] == device:
                self.running.remove(key)
        
    """ To switch on LED in Robotic ARM """
    def led_on(self, led):
        fd= open(led, "w")
        fd.write("1")
        fd.close()

    def led_off(self, led):
        fd= open(led, "w")
        fd.write("0")
        fd.close()

if __name__ == '__main__':
    arm = Arm()
    usb_dev_name = arm.find_usb_device()
    audioThread = thread.start_new_thread(arm.setupAudioStream,())

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
    arm.led_on(led)
    time.sleep(1)
    arm.led_off(led)
        
    # Move the grip 
    print "Grip control"
    grip= robotic_arm_path+"gripmotor"
    arm.move_clockwise(grip, 1)
    arm.move_anti_clockwise(grip, 1)
    arm.stop(grip)

    # Move the base 
    print "Base Motor control"
    base= robotic_arm_path+"basemotor"
    arm.move_clockwise(base, 2)
    arm.move_anti_clockwise(base, 2)
    arm.stop(base)

    # Move the Wrist
    print "Wrist Motor control"
    wrist= robotic_arm_path+"motor2"
    arm.move_clockwise(wrist, 1)
    arm.move_anti_clockwise(wrist, 1)
    arm.stop(wrist)

    # Move the Elbow
    print "Elbow Motor control"
    elbow= robotic_arm_path+"motor3"
    arm.move_clockwise(elbow, 1)
    arm.move_anti_clockwise(elbow, 1)
    arm.stop(elbow)

    # Move the Shoulder
    print "Shoulder Motor control"
    shoulder= robotic_arm_path+"motor4"
    arm.move_clockwise(shoulder, 1)
    arm.move_anti_clockwise(shoulder, 1)
    arm.stop(shoulder)