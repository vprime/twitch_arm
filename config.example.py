#!/usr/bin/python
audio_device = 0
threshold = 6000

channels = [
    'twitch_channel',
    ]
username = 'twitch_user'
oauth = 'oauth token'
clientId = ''
channel_id = ''

seq_throw = {
	"shoulder":[("1", 9), ("2", 6), ],
	"elbow":[("1", 9), ("2", 6),],
	"wrist":[("1", 4), ("0", 5), ("0", 2), ("0", 4),],
	"grip":[("0", 15), ("2", 2)],
}