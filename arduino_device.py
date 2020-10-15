#!python3

# Importing our required libaries
# Makes serial communication easy
import serial
import time
import json
import asyncio
from pprint import pprint

class message:
  def __init__(self):
    self.motors = []
    self.leds = []
  
  def add_motor(self, motor_id, speed):
    self.motors.append({"id": motor_id, "speed": speed})
  
  def add_led(self, led_id, color):
    self.leds.append({"id": led_id, "color": color})

  def clear(self):
    self.motors = []
    self.leds = []
  
  def serialize(self):
    return json.dumps({"motors":self.motors, "leds": self.leds})
  
  def flush(self):
    response = self.serialize()
    self.clear()
    return response

class device:
  def __init__(self):
    self._fps = 10
    self.message = message()
    self.connection = serial.Serial('/dev/serial0', 9600, timeout=10)
    self._running = True
    #asyncio.run(self.loop())
    
  async def loop(self):
    while self._running:
      # Loop through input averages
      self.send_events()
      # run this at the FPS
      await asyncio.sleep(1 / self._fps)

  def send_events(self):
    if not self.message:
      return
    self.send(self.message)

  def send(self, message):
    if not message:
      return
    print(message.serialize())
    self.connection.write((message.flush()+"\n").encode())
  
  def destroy(self):
    self.connection.close()
