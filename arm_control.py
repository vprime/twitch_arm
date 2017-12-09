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


@@ TODO
 - Add a sanity check for each motor and time ran.
   turn left & right don't give audable clicks, so having another limiter is essential.


"""

import os
import fnmatch
import sys
import time
from pprint import pprint

import audioop
import pyaudio

import thread

from pynput import keyboard

class Motor:
        name = ""
        device = ""
        maxTime = 0
        runTime = 0
        currentAction = "0"
        lastMove = "0"
        halted = False
        robotic_arm_path = ""
        count = 0

        STOP = "0"
        CLOCKWISE = "1"
        COUNTER_CLOCKWISE = "2"
        messages = []

        def __init__(self, motorData, robotic_arm_path):
            self.name = motorData[0]
            self.device = motorData[1]
            self.maxTime = motorData[2]
            self.robotic_arm_path = robotic_arm_path
            self.path = self.robotic_arm_path + self.device

        # Safely prevent the motor from traveling further.
        def halt(self):
            if self.checkMotor() != self.STOP:
                self.halted = True
                self.setAction(self.STOP)

        def forward(self, runTime):
            self.setAction(self.CLOCKWISE, runTime)

        def backward(self, runTime):
            self.setAction(self.COUNTER_CLOCKWISE, runTime)

        def checkMotor(self):
            fd = open(self.path, "r")
            current = fd.read()
            fd.close()
            return current.strip(' \t\n\r')

        # Record the action, and write to the motor
        def setAction(self, action, runTime = 0):
            if self.halted and action == self.lastMove:
                print "Unable to comply, motor halted: " + self.name
                return
            if self.halted and action != self.STOP:
                self.halted = False
            if action != self.STOP and action != self.lastMove:
                self.count = 0
            self.currentAction = action
            self.runTime = runTime
            self.count += runTime
            fd = open(self.path, "w")
            fd.write(action)
            self.start = time.time()
            fd.close()
            if action != self.STOP:
                self.lastMove = action

        # Runs constantly
        def update(self):
            state = self.checkMotor()
            # Stop the motor if it's halted
            if self.halted and state != self.STOP:
                self.setAction(self.STOP)
            # Check the time vs motor's start time
            now = time.time()
            if self.CLOCKWISE in state  or self.COUNTER_CLOCKWISE in state:
                if self.start + self.maxTime < now or self.start + self.runTime < now or self.count > self.maxTime:
                    self.setAction(self.STOP)

class Arm:
    chunk = 1024
    listening = True

    deviceMotors = [
        ["base", "basemotor", 12],
        ["grip", "gripmotor", 3],
        ["wrist", "motor2", 6],
        ["elbow", "motor3", 8],
        ["shoulder", "motor4", 8]
    ]

    robotic_arm_path= ""

    motors = []
    messages = []

    """ Locate the sysfs entry corresponding to USB Robotic ARM """
    def findUsbDevice(self):
        for file in os.listdir('/sys/bus/usb/drivers/robotic_arm/'):
            if fnmatch.fnmatch(file, '*:*'):
                self.robotic_arm_path = "/sys/bus/usb/drivers/robotic_arm/"+ file + "/"
                return file

    def setupMotors(self):
        for motorData in self.deviceMotors:
            motor = Motor(motorData, self.robotic_arm_path)
            self.motors.append(motor)
        motorUpdateThread = thread.start_new_thread(self.updateMotors, ())

    def setupAudioStream(self, inputDevice, threshold):
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
                    frames_per_buffer=self.chunk)
        self.listening = True
        while self.listening:
            data = stream.read(self.chunk, exception_on_overflow = False)
            rms = audioop.rms(data, 2)  #width=2 for format=paInt16
            if rms > threshold:
                print("RMS: " + str(rms))
                self.stopRunningMotors()
        stream.stop_stream()
        stream.close()
        p.terminate()

    # Run the update on motors
    def updateMotors(self):
        while True:
            for motor in self.motors:
                motor.update()
            time.sleep(0.01)

    def stopRunningMotors(self):
        for motor in self.motors:
            motor.halt()

    def resetHalts(self):
        for motor in self.motors:
            motor.halt = False
            motor.count = 0

    """ Run motors """
    def getMotor(self, name):
        for motor in self.motors:
            if motor.name == name:
                return motor

    def base(self, direction, time):
        motor = self.getMotor("base")
        if direction is "left":
            motor.backward(time)
        if direction is "right":
            motor.forward(time)

    def grip(self, direction, time):
        motor = self.getMotor("grip")
        if direction is "close":
            motor.forward(time)
        if direction is "open":
            motor.backward(time)

    def wrist(self, direction, time):
        motor = self.getMotor("wrist")
        if direction is "up":
            motor.forward(time)
        if direction is "down":
            motor.backward(time)

    def elbow(self, direction, time):
        motor = self.getMotor("elbow")
        if direction is "up":
            motor.forward(time)
        if direction is "down":
            motor.backward(time)

    def shoulder(self, direction, time):
        motor = self.getMotor("shoulder")
        if direction is "up":
            motor.forward(time)
        if direction is "down":
            motor.backward(time)

        
    """ To switch on LED in Robotic ARM """
    def led_on(self):
        led = self.robotic_arm_path + "led"
        fd= open(led, "w")
        fd.write("1")
        fd.close()

    def led_off(self):
        led = self.robotic_arm_path + "led"
        fd= open(led, "w")
        fd.write("0")
        fd.close()

    def getSoundOptions(self):
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    print "Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name')

    def on_press(self, key):
        try:
            print('alphanumeric key {0} pressed'.format(
                key.char))
            time = 2
            if key.char == "1":
                self.led_on()
            if key.char == "2":
                self.led_off()
            if key.char == "q":
                self.base("left", time)
            if key.char == "w":
                self.base("right", time)
            if key.char == "a":
                self.grip("open", time)
            if key.char == "s":
                self.grip("close", time)
            if key.char == "e":
                self.wrist("up", time)
            if key.char == "r":
                self.wrist("down", time)
            if key.char == "d":
                self.elbow("up", time)
            if key.char == "f":
                self.elbow("down", time)
            if key.char == "c":
                self.shoulder("up", time)
            if key.char == "v":
                self.shoulder("down", time)
        except AttributeError:
            print('special key {0} pressed'.format(
                key))

    def on_release(self, key):
        print('{0} released'.format(
            key))
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    def __init__(self, inputDevice=False, threshold=False):
        usb_dev_name = self.findUsbDevice()

        if ( usb_dev_name == None):
            print "Please ensure that robotic_arm module is loaded "
            print " Also ensure that you have connected the robotic arm "
            print " and switched on the Robotic ARM device"
            sys.exit(-1)

        self.setupMotors()
        if inputDevice is False:
            self.getSoundOptions()
            inputDevice = raw_input("Enter device ID: ")

        if threshold is False:
            threshold = raw_input("Threshold is: ")

        audioThread = thread.start_new_thread(self.setupAudioStream,(int(inputDevice), int(threshold)))

if __name__ == '__main__':
    arm = Arm()

    # Path for the robotic arm sysfs entries
    with keyboard.Listener(on_press=arm.on_press, on_release=arm.on_release) as listener:
        listener.join()