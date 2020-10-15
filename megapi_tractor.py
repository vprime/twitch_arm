import time, sys
import logging
import asyncio, threading
from pprint import pprint
from megapi import MegaPi


motorTime = 0.2
maxTime = 2.0
drivingSpeed = 150
armSpeed = 50
grabberSpeed = 50

LEFT_TRACK = 2
RIGHT_TRACK = 3
GRABBER = 4
ARM = 1

def setup():
    #Allocate the name 'RoboArm' to the USB device
    global megapiBot
    megapiBot = MegapiBot()

def move(args, time):
    try:
        megapiBot.handle_input(args, time)
    except:
        e = sys.exc_info()
        print("MegapiBot Error: " + str(e))


class MegapiBot:
    def __init__(self):
        self._prepare_motor_states()
        self.bot = MegaPi()
        self.bot.start()
        print("MegaPiBot Initialized")
        self.tsk = threading.Thread(target=self.main_loop, daemon=True)
        self.tsk.start()
        print("MegaPiBot Activated")

    def _prepare_motor_states(self):
        self.motors = {
            LEFT_TRACK: self._default_motor_state(LEFT_TRACK, -drivingSpeed, False),
            RIGHT_TRACK: self._default_motor_state(RIGHT_TRACK, drivingSpeed, False),
            GRABBER: self._default_motor_state(GRABBER, grabberSpeed, False),
            ARM: self._default_motor_state(ARM, armSpeed, True)
        }

    def handle_input(self, args, limit):
        global drivingSpeed
        command = args
        if limit > maxTime:
            limit = maxTime
        if limit < motorTime:
            limit = motorTime

        print("MegaPiBot Got command " + command + " limit:" + str(limit))
        if command == 'forward':
            self.drive(drivingSpeed, drivingSpeed, limit)
        if command == 'reverse':
            self.drive(-drivingSpeed, -drivingSpeed, limit)
        if command == 'left':
            self.drive(-drivingSpeed/2, drivingSpeed/2, limit)
        if command == 'right':
            self.drive(drivingSpeed/2, -drivingSpeed/2, limit)
        if command == 'close':
            self.move_motor(GRABBER, -grabberSpeed, limit)
        if command == 'open':
            self.move_motor(GRABBER, grabberSpeed, limit)
        if command == 'up':
            self.move_motor(ARM, -armSpeed, limit)
        if command == 'down':
            self.move_motor(ARM, armSpeed, limit)

    def main_loop(self):
        self.running = True
        print("MegapiBot Loop starting!")
        try:
            while self.running:
                self.update_motors()
                time.sleep(0.1)
        except Exception as e:
            print("MegapiBot Loop Error: " + str(e))

    def update_motors(self):
        for key in self.motors:
            self.update_motor(key)

    def _default_motor_state(self, motor, speed, encoder):
        return {
            'motor': motor,
            'defaultSpeed': speed,
            'currentSpeed': 0,
            'newSpeed': 0,
            'expire': 100,
            'encoder': encoder
        }

    def update_motor(self, motor_key):
        motor = self.motors[motor_key]
        if motor['newSpeed'] != motor['currentSpeed']:
            self.set_motor(motor_key, motor['newSpeed'])
        elif motor['currentSpeed'] != 0 and motor['expire'] < time.time():
            self.set_motor(motor_key, 0)

    def set_motor(self, motor_key, speed):
        motor = self.motors[motor_key]
        print("Running motor: " + str(motor_key) + " Speed: " + str(speed) + " Encoder: " + str(motor['encoder']) + " Time: " + str(time.time()) +" Expire: " + str(motor['expire']))
        if motor['encoder']:
            self.bot.encoderMotorRun(motor['motor'], speed)
        else:
            self.bot.motorRun(motor['motor'], speed)
        motor['currentSpeed'] = speed
        motor['newSpeed'] = speed
        #motor['expire'] = time.time() + motorTime
        self.motors[motor_key] = motor

    def drive(self, leftMotorSpeed, rightMotorSpeed, limit):
        global LEFT_TRACK, RIGHT_TRACK
        self.move_motor(LEFT_TRACK, int(leftMotorSpeed), limit)
        self.move_motor(RIGHT_TRACK, int(rightMotorSpeed), limit)

    def move_motor(self, motor, speed, limit):
        self.motors[motor]['newSpeed'] = speed
        self.motors[motor]['expire'] = time.time() + limit