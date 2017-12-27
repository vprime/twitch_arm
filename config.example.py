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


sequences ={
		"throw" :{
			"shoulder":[("1", 9), ("2", 6), ],
			"elbow":[("1", 9), ("2", 6),],
			"wrist":[("1", 4), ("0", 5), ("0", 2), ("0", 4),],
			"grip":[("0", 15), ("2", 2)],
		},

		"idle" :{
			"base":[("1", 2),("0", 5),("2", 2),],
			"wrist":[("0", 1.8),("2", 0.2),("0", 5),("1", 0.2),],
		},

		"yes":{
			"wrist":[("1", 0.5),("2", 0.4),("1", 0.5),("2", 0.4),],
		},
		"no":{
			"wrist":[("2", 0.2),("0", 3),("1", 0.3),],
			"base":[("1", 0.5),("2", 0.5),("1", 0.5),("2", 0.5),],
		},
	}

idles = ["idle",]

subscriber_sequences = {"throw":"throw", "yes":"yes", "no":"no", }

idle_wait = 300
idle_time = 30
powersave_time = 1800