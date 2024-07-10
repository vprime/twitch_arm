#!/usr/bin/python
""" 
Self Protecting OWI/Maplin USB Arm control
-----
Allows you to have a basic feedback loop using a microphone attached to the arm.
Listens for gearbox clicking, and halts movement to prevent damage.

Based on the robotic_arm_driver example here: 
https://github.com/maxinbjohn/robotic_arm_driver/blob/master/examples/python/motor.py

Author: Vincent Prime <myself@vincentprime.com>
--------------
LICENSE:


Modified MIT License

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

Restrictions:
    The software may not be used to operate nuclear facilities, life support 
    or other mission critical applications where human life or property may be at stake.
---------------

@@ TODO
 - Add a sanity check for each motor and time ran.
   turn left & right don't give audable clicks, so having another limiter is essential.


"""

import os
import fnmatch
import pprint
import sys
import time
from copy import deepcopy

import _thread


class Motor:
    name = ""
    device = ""
    max_time = 0
    min_time = 0.01
    run_time = 0
    current_action = "0"
    last_move = "0"
    halted = False
    robotic_arm_path = ""
    count = 0
    start = 0
    override = False
    max_run_time = 4.1

    STOP = "0"
    CLOCKWISE = "1"
    COUNTER_CLOCKWISE = "2"
    messages = []
    queue = []

    def __init__(self, motor_data, robotic_arm_path):
        self.name = motor_data[0]
        self.device = motor_data[1]
        self.max_time = motor_data[2]
        self.robotic_arm_path = robotic_arm_path
        self.path = self.robotic_arm_path + self.device

    # Safely prevent the motor from traveling further.
    def halt(self):
        if self.check_motor() != self.STOP:
            self.halted = True
            self.set_action(self.STOP)

    def forward(self, run_time):
        self.set_action(self.CLOCKWISE, run_time)

    def backward(self, run_time):
        self.set_action(self.COUNTER_CLOCKWISE, run_time)

    def check_motor(self):
        fd = open(self.path, "r")
        current = fd.read()
        fd.close()
        return current.strip(' \t\n\r')

    def set_queue(self, new):
        self.queue = new

    def next(self):
        if len(self.queue) > 0:
            action = self.queue.pop(0)
            self.set_action(action[0], action[1], True, True)

    # Record the action, and write to the motor
    def set_action(self, action, run_time=0.0, silent_message=False, override=False):
        if self.halted and action == self.last_move:
            print("Unable to comply, motor halted: " + self.name)
            if not silent_message:
                self.messages.append("Unable to comply, " + self.name + " motor halted in that direction. Reverse to release." )
            return
        if self.halted and action != self.STOP:
            self.halted = False
        if action != self.STOP and action != self.last_move:
            self.count = 0
        if action != self.STOP and self.count >= self.max_time and not silent_message:
            self.messages.append("Unable to comply, " + self.name + " has reached it's limit for that direction. Reverse to try again.")
        print("setting action to " + action)
        self.current_action = action
        if run_time > self.max_run_time:
            run_time = self.max_run_time
        self.run_time = run_time
        self.override = override
        if override:
            self.count += run_time
        else:
            self.count += min(run_time, self.max_time)
        self.start = time.time()
        if action != self.STOP:
            self.last_move = action

    # Runs constantly
    def update(self):
        state = self.check_motor()
        updating = False
        # Stop the motor if it's halted
        if self.halted and state != self.STOP:
            self.set_action(self.STOP)
        # Check the time vs motor's start time
        now = time.time()
        if self.CLOCKWISE in state or self.COUNTER_CLOCKWISE in state:
            if not self.override and self.start + self.max_time < now: 
                self.set_action(self.STOP)
            if self.run_time > self.min_time and self.start + self.run_time < now:
                self.set_action(self.STOP)
            if not self.override and self.count > self.max_time:
                self.set_action(self.STOP)
        # run queue
        if len(self.queue) > 0:
            if self.start + self.run_time < now:
                self.next()
        if self.current_action != state:
            updating = True
        return self.path, self.current_action, updating


def write_motor(path, action):
    fd = open(path, "w")
    fd.write(action)
    fd.close()


class Arm:
    chunk = 1024
    listening = True

    device_motors = [
        ["base", "basemotor", 30],
        ["grip", "gripmotor", 6],
        ["wrist", "motor2", 10],
        ["elbow", "motor3", 30],
        ["shoulder", "motor4", 30],
        ["light", "led", 30]
    ]

    messages = []
    paths = {}
    devices = {}
    paused = False

    def __init__(self, device_paths):
        self.paths = device_paths
        if len(self.paths) == 0:
            print("Please ensure that robotic_arm module is loaded ")
            print(" Also ensure that you have connected the robotic arm ")
            print(" and switched on the Robotic ARM device")
            sys.exit(-1)
        self.motor_update_thread = self.setup_motors()

    def remap_names(self, mapping):
        self.paused = True
        time.sleep(0.5)
        for (old, new) in mapping:
            self.devices[new] = self.devices.pop(old)
        self.paused = False

    def setup_motors(self):
        for device, path in self.paths.items():
            self.devices[device] = []
            for motor_data in self.device_motors:
                motor = Motor(motor_data, path)
                self.devices[device].append(motor)
        pprint.pprint(self.devices)
        return _thread.start_new_thread(self.update_motors, ())

    # Run the update on motors
    def update_motors(self):
        while True:
            if self.paused:
                time.sleep(1)
                continue
            for device_name, device_motors in self.devices.items():
                for motor in device_motors:
                    (path, action, updated) = motor.update()
                    if updated:
                        print("writing motor: " + path + " Action: " + action)
                        write_motor(path, action)
                    if len(motor.messages) > 0:
                        self.messages.append(motor.messages.pop(0))
            time.sleep(0.1)

    def stop_running_motors(self):
        for device in self.devices:
            for motor in device:
                motor.halt()

    def reset_halts(self):
        for device in self.devices:
            for motor in device:
                motor.halted = False
                motor.count = 0

    """ Run motors """
    def get_motor(self, name, device_name):
        for motor in self.devices[device_name]:
            if motor.name == name or motor.device == name:
                return motor

    def drive(self, motor, direction, duration, device):
        motor = self.get_motor(motor, device)
        motor.set_action(direction, duration)

    # Turns the base left, and right, over a given time.
    def base(self, direction, duration, device):
        motor = self.get_motor("base", device)
        if direction == "left":
            motor.backward(duration)
        if direction == "right":
            motor.forward(duration)

    def grip(self, direction, duration, device):
        motor = self.get_motor("grip", device)
        if direction == "close":
            motor.forward(duration)
        if direction == "open":
            motor.backward(duration)

    def wrist(self, direction, duration, device):
        motor = self.get_motor("wrist", device)
        if direction == "up":
            motor.forward(duration)
        if direction == "down":
            motor.backward(duration)

    def elbow(self, direction, duration, device):
        motor = self.get_motor("elbow", device)
        if direction == "up":
            motor.forward(duration)
        if direction == "down":
            motor.backward(duration)

    def shoulder(self, direction, duration, device):
        motor = self.get_motor("shoulder", device)
        if direction == "up":
            motor.forward(duration)
        if direction == "down":
            motor.backward(duration)

    def sequence(self, sequence_matrix, device):
        self.reset_halts()
        for motor_name, motor_actions in sequence_matrix.iteritems():
            m = self.get_motor(motor_name, device)
            m.set_queue(deepcopy(motor_actions))
