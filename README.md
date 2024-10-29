# Twitch Robot Controller

This project provides a twitch chat interface for the OWI Robotic arm,
as well as megapi. It is intended to run on Raspberry Pi, but can be 
used on any linux computer.

## Setup
If you're using a camera, I reccomend first installing mjpg_streamer. it provides
a fast low latency stream you can injest into your streaming software of choice.

### Setup Python
- Requires Python 3.12
- Download Python, extract the folder.
- Enter the folder and run the commands
```
sudo make -j 4
sudo make altinstall
```
- run `python3.8 -V` to verify you have the right version.

### Setup Drivers
- Download the robotic_arm_driver submodule
- Install your kernel headers this will require
```
sudo apt install build-essential raspberrypi-kernel-headers
```
- Then compile the driver
```
cd ./robotic_arm_driver
make
```
- This should output a robotic_arm.ko file that will be used as the arm's driver.


### Configuration
- open the twitch_arm/ directory
- create a .env file with the following variables
```
# ./.env
TMI_TOKEN=oauth:abcd123 	# Twitch oauth key
CLIENT_ID=oinhaoifsas 		# Twitch client id
BOT_NICK=my_twitch_robot 	# Twitch client nickname, this matches the bots screename
BOT_PREFIX=! 				# The character that will prefix all the bot commands.
CHANNEL=my_twitch_channel 	# The channel the bot will join.
```
- Edit the TwitchBot.service file so `WorkingDirectory=` is the same directory as start.sh, and `ExecStart=` points to start.sh.
- Commands can be configured in the bot.py file.

### Running the bot manually
- Install the kernel module `insmod robotic_arm_driver/robotic_arm.ko`
- Configure permissions on the devices `sudo chmod -R 777 /sys/bus/usb/drivers/robotic_arm/*`
- Run the bot `pipenv run python bot.py`
- The script will search for available devices, and move one at a time and ask for an "l" or "r" to define the left and right arm.
- Once the devices are discovered, you will see a message "Logged in as | <USERNAME>". Your robot is now online!

### Setup Run on boot
- Copy the service file into systemd
```
sudo cp TwitchBot.service /etc/systemd/system/TwitchBot.service
```
- Reload the daemon, and enable the service.
```
sudo systemctl daemon-reload
sudo systemctl enable TwitchBot
```

### Running the bot rom systemctl
- Start the service.
```
sudo systemctl start TwitchBot
```
- Check on the bot's status
```
sudo systemctl status TwitchBot
```


## Twitch Commands
All movement commands can be ammended with a time in seconds to run.
- `!gripopen`  `!go` Opens the grabber
- `!gripclose`  `!gc` Closes the grabber
- `!baseleft`  `!bl` Turns the base left
- `!baseright`  `!br` Turns the base right
- `!wristup`  `!wu` Tilts the wrist up
- `!wristdown`  `!wd` Tilts the wrist down
- `!elboup`  `!eu` Tilts the elbow up
- `!elbowdown `  `!ed` Tilts the elbow down
- `!shoulderup`  `!su` Tilts the shoulder up
- `!shoulderdown`  `!sd` Tilts the shoulder down

