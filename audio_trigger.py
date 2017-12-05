#!/usr/bin/python
# 
# Sound Trigger
# Refrence: https://stackoverflow.com/questions/2668442/detect-and-record-a-sound-with-python
# 

import audioop
import pyaudio
import sys

def calibrate(testAction):
    getSoundOptions()
    device = input("Enter Input Device id: ")
    ## Need to find the mode and upper range
    ## Listen on sound, store RMS values in array
    ## run till testAction returns true
    rmsData = []
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
                input_device_index=device,
                frames_per_buffer=chunk)

    testComplete = False
    while not testComplete:
        data = stream.read(chunk)
        # check level against threshold, you'll have to write getLevel()
        rms = audioop.rms(data, 2)  #width=2 for format=paInt16
        rmsData.append(rms)
        testComplete = 

    stream.stop_stream()
    stream.close()
    p.terminate()


def runOnSound(inputDevice, threshold, callback):
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

    while True:
        data = stream.read(chunk)
        # check level against threshold, you'll have to write getLevel()
        rms = audioop.rms(data, 2)  #width=2 for format=paInt16
        if rms > threshold:
            callback()
            break

    stream.stop_stream()
    stream.close()
    p.terminate()


def getSoundOptions():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print "Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name')
    