# Robotic Arm Controller with Twitch.tv Chat Control and Audio Feedback Loop

Connects the OWI Robot Arm to Twitch, uses audio feedback to prevent gearbox damage.

Twitch Client Based on work by LynnAU under the MIT License
https://github.com/LynnAU/Twitch-Chat-Bot-V2

Arm Controller Based on the robotic_arm_driver example here: 
https://github.com/maxinbjohn/robotic_arm_driver/blob/master/examples/python/motor.py

## Requirements:
- OWI Robotic Arm
- USB kit for your Arm
- Microphone
- GNU/Linux
- python
- pyaudio
- pynput
- robotic_arm_driver - https://github.com/maxinbjohn/robotic_arm_driver


## Setup:

Install the robotic_arm_driver as per instructions here: https://github.com/maxinbjohn/robotic_arm_driver

Build the arm, and install the USB kit.
Attach a microphone to your arm, plug the microphone into your computer.

Copy `config.example.py` to `config.py`, edit file with desired parameters.

`audioDevice` is the device index (interger) from the list output when you run `arm_control.py` directly
`threshold` is an interger of the RMS (Root-Mean-Square) on which will trigger the motor to stop

To determine the best values, run `./arm_control.py` 
It will allow you to test audio devices, arm connectivity, and threshold values.
After you enter setup values, you're able to control the arm with your keyboard and you'll see RMS output when it triggers a stop on the motors.

take note of the values that work and set them in config.py.

`username` variable is your twitch username
`oauth` variable is your OAuth Token, you may generate one using this tool https://twitchapps.com/tmi/
The format should look something like "oauth:mLtoomhN6rJAJQDHR1vZzPN5hVJDL1" (That's not a real one, just an example. This Token is private.)

`channels` variable is a list of the twitch channels which your bot should listen on.

after configuration is complete, run `./twitch_client.py` to begin accepting input from twitch.

### arm_control.py Keyboard Controls
- LED: 1, 2
- Rotate base: q, w
- Grip: a, s
- Wrist: e, r
- Elbow: d, f
- Shoulder: c, v
- Quit: Esc

## Twitch Commands
- `!ping` a connection test
- `!light on` Turns on the LED
- `!light off` Turns off the LED
- `!left` rotate base left
- `!right` rotate base right
- `!grab` closes grip
- `!drop` opens grip
- `!wrist down` tilts wrist down
- `!wrist up` tilts wrist up
- `!elbow down` bends elbow down
- `!elbow up` bends elbow up
- `!shoulder down` bends shoulder down
- `!shoulder up` bends shoulder up