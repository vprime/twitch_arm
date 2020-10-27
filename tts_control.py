#!python3
import time, sys
import asyncio, threading
from pprint import pprint
import asyncio
import pyttsx3
import queue

def setup_speak():
    #Allocate the name 'RoboArm' to the USB device
    global chatSpeaker
    chatSpeaker = ChatSpeaker()

def speak(args):
    try:
        chatSpeaker.handle_input(args)
    except:
        e = sys.exc_info()
        print("ChatSpeaker Error: " + str(e))


class ChatSpeaker:
    # 
    def __init__(self):
        self.messages = queue.Queue()
        self.engine = pyttsx3.init()
        print("ChatSpeaker Initialized")
        self.tsk = threading.Thread(target=self.main_loop, daemon=True)
        self.tsk.start()
        print("ChatSpeaker Activated")

    def handle_input(self, args):
        self.messages.put(args)
        

    def main_loop(self):
        self.running = True
        print("ChatSpeaker Loop starting!")
        try:
            while self.running:
                self.update_speakers()
                time.sleep(0.1)
        except Exception as e:
            print("ChatSpeaker Loop Error: " + str(e))

    def update_speakers(self):
        while not self.messages.empty():
            self.update_speaker(self.messages.get())

    # Get motor data from buffer, and set to the motor
    def update_speaker(self, message):
        self.engine.say(message)
        self.engine.runAndWait()