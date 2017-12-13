#!/usr/bin/python
'''
Based on work by LynnAU under the MIT License
https://github.com/LynnAU/Twitch-Chat-Bot-V2

This is a framework for a Bot configured for Twitch
Using this will require some knowledge of Python since there are no commands
to begin with, once the username, channels and oauth has been filled out. The
program will just print out the chat of the channels it connects to.
You can send a message by using the following function,
sendmsg(chan,msg)
--
chan = The channel you want to send the message to, make sure it has a #
in front of it (String)
msg = The message you want to send to the channel, must be a string
--
sendwhis(user,msg)
--
user = The username of the person you want to send the message to (String)
msg = The message you want to send to the user, must be a string
--


@@ TODO
 - Allow user to set time
 - Rate Limiter
 - Rate Limit White List
 - Admin List
 - Subscription for White List

'''




# Import necessary libraries.
import datetime
import socket
import select
import re
import config
import time
from arm_control import Arm

''' Change the following settings if you wish to run the program '''
channels = []
username = ''
oauth = ''


# Definitions to use while connected
def ping():
    ''' Respond to the server 'pinging' (Stays connected) '''
    socks[0].send('PONG :pingis\n')
    print('PONG: Client > tmi.twitch.tv')

def sendmsg(chan,msg):
    ''' Send specified message to the channel '''
    socks[0].send('PRIVMSG '+chan+' :'+msg+'\n')
    print('[BOT] -> '+chan+': '+msg+'\n')

def sendwhis(user,msg):
    socks[1].send('PRIVMSG #jtv :/w '+user+' '+msg+'\n')
    print('[BOT] -> '+user+': '+msg+'\n')

def getmsg(msg):
    ''' GET IMPORTANT MESSAGE '''
    if(re.findall('@(.*).tmi.twitch.tv PRIVMSG (.*) :(.*)',msg)):
        msg_edit = msg.split(':',2)
        if(len(msg_edit) > 2):
            user = msg_edit[1].split('!',1)[0] # User
            message = msg_edit[2] # Message
            channel = re.findall('PRIVMSG (.*)',msg_edit[1]) # Channel

            privmsg = re.findall('@(.*).tmi.twitch.tv PRIVMSG (.*) :(.*)',msg)
            ''' CONVERT TO ARRAY '''
            privmsg = [x for xs in privmsg for x in xs]

            datelog = datetime.datetime.now()

            ''' PRINT TO CONSOLE '''
            if(len(privmsg) > 0):
                print('['+str(datelog.hour)+':'+str(datelog.minute)+':'+str(datelog.second)+'] '+user+' @ '+channel[0][:-1]+': '+message)
                
    if(re.findall('@(.*).tmi.twitch.tv WHISPER (.*) :(.*)',msg)):
        whisper = re.findall('@(.*).tmi.twitch.tv WHISPER (.*) :(.*)',msg)
        whisper = [x for xs in whisper for x in xs]

        ''' PRINT TO CONSOLE '''
        if(len(whisper) > 0):
            ''' PRINT WHISPER TO CONSOLE '''
            print('*WHISPER* '+whisper[0]+': '+whisper[2])
def float_or_def(string, default):
    if(any(str.isdigit(c) for c in string)):
        numbers = re.findall("\d+\.\d+|.\d|\d", string)
        return float(numbers[0])
    return default

def int_or_def(string, default):
    if(any(str.isdigit(c) for c in string)):
        return int(filter(str.isdigit, string))
    return default

def command(cmd, arm, user):
    cmd = cmd.lower()
    global solo_user, solo_time, solo_start, username
    # Ignore nightbot commands
    if(cmd.startswith("!filters") or cmd.startswith("!poll") or cmd.startswith("!regulars") or cmd.startswith("!songs") or cmd.startswith("!winner")):
        return
    if(solo_user and time.time() < solo_start + solo_time and user != username):
        if(user != solo_user):
            return
    if(cmd == "!ping"):
        sendmsg(channel, "Pong!")
        return
    if(cmd == "!light on" or cmd == "!led on"):
        arm.led_on()
        return
    if(cmd == "!light off" or cmd == "!led off"):
        arm.led_off()
        return
    if(cmd.startswith("!left")):
        arm.base("left", float_or_def(cmd, 2))
        return
    if(cmd.startswith("!right")):
        arm.base("right", float_or_def(cmd, 2))
        return
    if(cmd.startswith("!grab") or cmd.startswith("!close")):
        arm.grip("close", float_or_def(cmd, 1.8))
        return
    if(cmd.startswith("!drop") or cmd.startswith("!open")):
        arm.grip("open", float_or_def(cmd, 1.8))
        return
    if(cmd.startswith("!wrist down")):
        arm.wrist("down", float_or_def(cmd, 2))
        return
    if(cmd.startswith("!wrist up")):
        arm.wrist("up", float_or_def(cmd, 2))
        return
    if(cmd.startswith("!elbow down")):
        arm.elbow("down", float_or_def(cmd, 1.5))
        return
    if(cmd.startswith("!elbow up")):
        arm.elbow("up", float_or_def(cmd, 2))
        return
    if(cmd.startswith("!shoulder down")):
        arm.shoulder("down", float_or_def(cmd, 1.5))
        return
    if(cmd.startswith("!shoulder up")):
        arm.shoulder("up", float_or_def(cmd, 2))
        return
    if(cmd.startswith("!reset") and user == username):
        arm.reset_halts()
        return
    if(cmd.startswith("!threshold") and user == username):
        arm.threshold = float_or_def(cmd, 10000)
        return
    if(cmd.startswith("!solo") and user == username):
        exp = cmd.split(' ')
        solo_user = exp[1]
        solo_time = float_or_def(exp[2], 30)
        sendmsg(channel, "Giving control to " + solo_user + " for " + str(solo_time) + " seconds")
        solo_start = time.time()
        return
    if(cmd.startswith("!clearsolo") and user == username):
        solo_user = ""
        solo_time = 0
        sendmsg(channel, "Giving control back to Twitch!")
        return
    if(cmd.startswith("!com") or cmd.startswith("!help")):
        sendmsg(channel, "Arm Commands: !<motor> <direction> <seconds 1-4>  Actions Available: led (on off), left, right, grab, drop, wrist (up down), elbow (up down), shoulder (up down)")
        return
    if cmd.startswith("!"):
        sendmsg(channel, "Not a command I understand, try !help")

if __name__ == '__main__':
    arm = Arm(config.audio_device, config.threshold)
    
    channels = config.channels
    username = config.username
    oauth = config.oauth

    solo_user = ''
    solo_time = 0
    solo_start = 0

    # Connect to the server using the provided details
    socks = [socket.socket()]
    ''' Connect to the server using port 6667 & 443 '''
    socks[0].connect(('irc.chat.twitch.tv',6667))
    #socks[1].connect(('GROUP_CHAT_IP',GROUP_CHAT_PORT))

    '''Authenticate with the server '''
    socks[0].send('PASS '+oauth+'\n')
    #socks[1].send('PASS OAUTH_TOKEN\n')
    ''' Assign the client with the nick '''
    socks[0].send('NICK '+username+'\n')
    #socks[1].send('NICK USER\n')
    ''' Join the specified channel '''
    for val in channels:
        socks[0].send('JOIN #'+val+'\n')
    print(socks[0].recv(2048))
    #socks[1].send('JOIN GROUP_CHAT_CHANNEL\n')

    ''' Send special requests to the server '''
    # Used to recieve and send whispers!
    #socks[1].send('CAP REQ :twitch.tv/commands\n')

    print('Connected to irc.twitch.tv on port 6667')
    print('USER: '+username)
    print('OAUTH: oauth:'+'*'*30)
    print('\n')

    temp = 0
    while True:
        (sread,swrite,sexc) = select.select(socks,socks,[],120)
        # Echo the messages to the channel                   
        if(len(arm.messages) > 0):
            sendmsg(channel, arm.messages.pop(0))
        for sock in sread:    
            ''' Receive data from the server '''
            msg = sock.recv(2048)
            if(msg == ''):
                temp + 1
                if(temp > 5):
                    print('Connection might have been terminated')
        
            ''' Remove any linebreaks from the message '''
            msg = msg.strip('\n\r')

            ''' DISPLAY MESSAGE IN SHELL '''
            getmsg(msg)

            # ANYTHING TO DO WITH CHAT FROM CHANNELS
            ''' GET THE INFO FROM THE SERVER '''
            check = re.findall('@(.*).tmi.twitch.tv PRIVMSG (.*) :(.*)',msg)
            if(len(check) > 0):
                msg_edit = msg.split(':',2)
                if(len(msg_edit) > 2):
                    user = msg_edit[1].split('!',1)[0] # User
                    message = msg_edit[2] # Message
                    channel = msg_edit[1].split(' ',2)[2][:-1] # Channel
                    #print(message)
                    #msg_split = str.split(message)
                    command(message, arm, user)
                            
            # ANYTHING TO DO WITH WHISPERS RECIEVED FROM USERS
            check = re.findall('@(.*).tmi.twitch.tv WHISPER (.*) :(.*)',msg)
            if(len(check) > 0):
                msg_edit = msg.split(':',2)
                if(len(msg) > 2):
                    user = msg_edit[1].split('!',1)[0] # User
                    message = msg_edit[2] # Message
                    channel = msg_edit[1].split(' ',2)[2][:-1] # Channel

                    whis_split = str.split(message)
            
            ''' Respond to server pings '''
            if msg.find('PING :') != -1:
                print('PING: tmi.twitch.tv > Client')
                ping()