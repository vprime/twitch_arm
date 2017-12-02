#!/usr/bin/python
# 
# Sound Triggering Tests
# Refrence: https://stackoverflow.com/questions/2668442/detect-and-record-a-sound-with-python
# 

import audioop
import pyaudio
import sys

def listenForSound(inputDevice, threshold):
    chunk = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 5
    
    p = pyaudio.PyAudio()
    
    stream = p.open(format=FORMAT,
                channels=CHANNELS, 
                rate=RATE, 
                input=True,
                output=True,
                input_device_index=inputDevice,
                frames_per_buffer=chunk)

    print "* recording"
    while True:
        data = stream.read(chunk)
        # check level against threshold, you'll have to write getLevel()
        rms = audioop.rms(data, 2)  #width=2 for format=paInt16
        print rms
        if rms > threshold:
           break

    print "* done"

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
    