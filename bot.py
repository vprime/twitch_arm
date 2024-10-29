# bot.py
import math
import os
import re
import fnmatch
from twitchio.ext import commands, routines
from arm_control import Arm

# Arm Device Names
BASE = "basemotor"
GRIP = "gripmotor"
WRIST = "motor2"
ELBOW = "motor3"
SHOULDER = "motor4"
LIGHT = "led"
LEFTARM = "l"
RIGHTARM = "r"

# Device Commands
STOP = "0"
CLOCKWISE = "1"
COUNTER_CLOCKWISE = "2"

# Directional Mapping
UP = CLOCKWISE
DOWN = COUNTER_CLOCKWISE
LEFT = COUNTER_CLOCKWISE
RIGHT = CLOCKWISE
OPEN = COUNTER_CLOCKWISE
CLOSE = CLOCKWISE


# Twitch bot
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.environ['TMI_TOKEN'],
            prefix=os.environ['BOT_PREFIX'],
            initial_channels=[os.environ['CHANNEL']],
        )

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        print(message.content)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command(name='leftgripopen', aliases=['lgo'])
    async def arm_l_gopen(self, ctx: commands.Context):
        await write_motor(ctx, LEFTARM, GRIP, OPEN, fod(ctx.message.content, 1.0))

    @commands.command(name='leftgripclose', aliases=['lgc'])
    async def arm_l_gclose(self, ctx: commands.Context):
        await write_motor(ctx, LEFTARM, GRIP, CLOSE, fod(ctx.message.content, 1.0))

    @commands.command(name='leftbaseleft', aliases=['lbl'])
    async def arm_l_bleft(self, ctx: commands.Context):
        await write_motor(ctx, LEFTARM, BASE, LEFT, fod(ctx.message.content, 1.0))

    @commands.command(name='leftbaseright', aliases=['lbr'])
    async def arm_l_bright(self, ctx: commands.Context):
        await write_motor(ctx, LEFTARM, BASE, RIGHT, fod(ctx.message.content, 1.0))

    @commands.command(name='leftwristup', aliases=['lwu'])
    async def arm_l_wup(self, ctx: commands.Context):
        await write_motor(ctx, LEFTARM, ELBOW, DOWN, fod(ctx.message.content, 1.0))

    @commands.command(name='leftwristdown', aliases=['lwd'])
    async def arm_l_wdown(self, ctx: commands.Context):
        await write_motor(ctx, LEFTARM, ELBOW, UP, fod(ctx.message.content, 1.0))

    @commands.command(name='leftelbowup', aliases=['leu'])
    async def arm_l_eup(self, ctx: commands.Context):
        await write_motor(ctx, LEFTARM, WRIST, DOWN, fod(ctx.message.content, 1.0))

    @commands.command(name='leftelbowdown', aliases=['led'])
    async def arm_l_edown(self, ctx: commands.Context):
        await write_motor(ctx, LEFTARM, WRIST, UP, fod(ctx.message.content, 1.0))

    @commands.command(name='leftshoulderup', aliases=['lsu'])
    async def arm_l_sup(self, ctx: commands.Context):
        await write_motor(ctx, LEFTARM, SHOULDER, UP, fod(ctx.message.content, 1.0))

    @commands.command(name='leftshoulderdown', aliases=['lsd'])
    async def arm_l_sdown(self, ctx: commands.Context):
        await write_motor(ctx, LEFTARM, SHOULDER, DOWN, fod(ctx.message.content, 1.0))

    @commands.command(name='rightgripopen', aliases=['rgo'])
    async def arm_r_gopen(self, ctx: commands.Context):
        await write_motor(ctx, RIGHTARM, GRIP, OPEN, fod(ctx.message.content, 1.0))

    @commands.command(name='rightgripclose', aliases=['rgc'])
    async def arm_r_gclose(self, ctx: commands.Context):
        await write_motor(ctx, RIGHTARM, GRIP, CLOSE, fod(ctx.message.content, 1.0))

    @commands.command(name='rightbaseleft', aliases=['rbl'])
    async def arm_r_bleft(self, ctx: commands.Context):
        await write_motor(ctx, RIGHTARM, BASE, LEFT, fod(ctx.message.content, 1.0))

    @commands.command(name='rightbaseright', aliases=['rbr'])
    async def arm_r_bright(self, ctx: commands.Context):
        await write_motor(ctx, RIGHTARM, BASE, RIGHT, fod(ctx.message.content, 1.0))

    @commands.command(name='rightwristup', aliases=['rwu'])
    async def arm_r_wup(self, ctx: commands.Context):
        await write_motor(ctx, RIGHTARM, ELBOW, DOWN, fod(ctx.message.content, 1.0))

    @commands.command(name='rightwristdown', aliases=['rwd'])
    async def arm_r_wdown(self, ctx: commands.Context):
        await write_motor(ctx, RIGHTARM, ELBOW, UP, fod(ctx.message.content, 1.0))

    @commands.command(name='rightelbowup', aliases=['reu'])
    async def arm_r_eup(self, ctx: commands.Context):
        await write_motor(ctx, RIGHTARM, WRIST, DOWN, fod(ctx.message.content, 1.0))

    @commands.command(name='rightelbowdown', aliases=['red'])
    async def arm_r_edown(self, ctx: commands.Context):
        await write_motor(ctx, RIGHTARM, WRIST, UP, fod(ctx.message.content, 1.0))

    @commands.command(name='rightshoulderup', aliases=['rsu'])
    async def arm_r_sup(self, ctx: commands.Context):
        await write_motor(ctx, RIGHTARM, SHOULDER, UP, fod(ctx.message.content, 1.0))

    @commands.command(name='rightshoulderdown', aliases=['rsd'])
    async def arm_r_sdown(self, ctx: commands.Context):
        await write_motor(ctx, RIGHTARM, SHOULDER, DOWN, fod(ctx.message.content, 1.0))

    @commands.command(name='help', aliases=['h', 'cmd', 'command', 'commands', 'man', 'manual'])
    async def help(self, ctx: commands.Context):
        message = '''
        \n\r **Left arm:**
        \n\r - Grip: !lgo, !lgc
        \n\r - Wrist: !lwu, !lwd
        \n\r - Elbow: !leu, !led
        \n\r - Shoulder: !lsu, !lsd
        \n\r - Base: !lbr, !lbl
        \n\r
        \n\r **Right arm:**
        \n\r - Grip: !rgo, !rgc
        \n\r - Wrist: !rwu, !rwd
        \n\r - Elbow: !reu, !red
        \n\r - Shoulder: !rsu, !rsd
        \n\r - Base: !rbr, !rbl
        '''
        await ctx.send(message)

    @routines.routine(minutes=3)
    async def reset_arm(self):
        # Every 3 minutes
        # Clear movement counters on the arm
        arm.reset_halts()


# Write to the arm device
async def write_motor(ctx: commands.Context, device, motor, action, time):
    if math.isnan(time):
        time = 1.0
    if time < 0.1:
        time = 0.1
    if arm is not None:
        arm.drive(motor, action, time, device)
        while len(arm.messages) > 0:
            message = arm.messages.pop(0)
            await ctx.send(message)

# Float or Default
# Find a number, or return the default
def fod(string, default):
    print("Finding numbers in: " + string)
    if any(str.isdigit(c) for c in string):
        numbers = re.findall(r'\d+[.|,]\d+|[.|,]\d|\d\d|\d', string)
        return float(numbers[0])
    return default

# Find USB devices that should match the device we're using
def find_usb_devices():
    result = {}
    for file in os.listdir('/sys/bus/usb/drivers/robotic_arm/'):
        if fnmatch.fnmatch(file, '*:*'):
            result[file] = "/sys/bus/usb/drivers/robotic_arm/"+ file + "/"
    return result


arm = Arm(find_usb_devices())

# Loop through found devices, assign them to left or right values.
def setup_arms():
    new_keys = []
    for key, value in arm.devices.items():
        print("Setup arm: " + key)
        arm.drive(BASE, RIGHT, 0.5, key)
        arm_name = input("Select arm that moved (l/r):")
        print("Chosen: " + arm_name)
        new_keys.append((key, arm_name))
    arm.remap_names(new_keys)

# Main program
if __name__ == "__main__":
    setup_arms()
    bot = Bot()
    bot.run()
