# bot.py
import math
import os
import re
import fnmatch
from twitchio.ext import commands
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

#
# bot = commands.Bot(
#     # set up the bot
#     token=os.environ['TMI_TOKEN'],
#     client_id=os.environ['CLIENT_ID'],
#     nick=os.environ['BOT_NICK'],
#     prefix=os.environ['BOT_PREFIX'],
#     initial_channels=[os.environ['CHANNEL']]
# )
#
#
# @bot.event
# async def event_ready():
#     """Called once when the bot goes online."""
#     print(f"{os.environ['BOT_NICK']} is online!")
#
#
# @bot.event
# async def event_message(ctx):
#     'Runs every time a message is sent in chat.'
#     await bot.handle_commands(ctx)
#     # make sure the bot ignores itself and the streamer
#     if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
#         return




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
        write_motor(LEFTARM, GRIP, OPEN, fod(ctx.message.content, 1.0))

    @commands.command(name='leftgripclose', aliases=['lgc'])
    async def arm_l_gclose(self, ctx: commands.Context):
        write_motor(LEFTARM, GRIP, CLOSE, fod(ctx.message.content, 1.0))

    @commands.command(name='leftbaseleft', aliases=['lbl'])
    async def arm_l_bleft(self, ctx: commands.Context):
        write_motor(LEFTARM, BASE, LEFT, fod(ctx.message.content, 1.0))

    @commands.command(name='leftbaseright', aliases=['lbr'])
    async def arm_l_bright(self, ctx: commands.Context):
        write_motor(LEFTARM, BASE, RIGHT, fod(ctx.message.content, 1.0))

    @commands.command(name='leftwristup', aliases=['lwu'])
    async def arm_l_wup(self, ctx: commands.Context):
        write_motor(LEFTARM, ELBOW, DOWN, fod(ctx.message.content, 1.0))

    @commands.command(name='leftwristdown', aliases=['lwd'])
    async def arm_l_wdown(self, ctx: commands.Context):
        write_motor(LEFTARM, ELBOW, UP, fod(ctx.message.content, 1.0))

    @commands.command(name='leftelbowup', aliases=['leu'])
    async def arm_l_eup(self, ctx: commands.Context):
        write_motor(LEFTARM, WRIST, DOWN, fod(ctx.message.content, 1.0))

    @commands.command(name='leftelbowdown', aliases=['led'])
    async def arm_l_edown(self, ctx: commands.Context):
        write_motor(LEFTARM, WRIST, UP, fod(ctx.message.content, 1.0))

    @commands.command(name='leftshoulderup', aliases=['lsu'])
    async def arm_l_sup(self, ctx: commands.Context):
        write_motor(LEFTARM, SHOULDER, UP, fod(ctx.message.content, 1.0))

    @commands.command(name='leftshoulderdown', aliases=['lsd'])
    async def arm_l_sdown(self, ctx: commands.Context):
        write_motor(LEFTARM, SHOULDER, DOWN, fod(ctx.message.content, 1.0))

    @commands.command(name='rightgripopen', aliases=['rgo'])
    async def arm_r_gopen(self, ctx: commands.Context):
        write_motor(RIGHTARM, GRIP, OPEN, fod(ctx.message.content, 1.0))

    @commands.command(name='rightgripclose', aliases=['rgc'])
    async def arm_r_gclose(self, ctx: commands.Context):
        write_motor(RIGHTARM, GRIP, CLOSE, fod(ctx.message.content, 1.0))

    @commands.command(name='rightbaseleft', aliases=['rbl'])
    async def arm_r_bleft(self, ctx: commands.Context):
        write_motor(RIGHTARM, BASE, LEFT, fod(ctx.message.content, 1.0))

    @commands.command(name='rightbaseright', aliases=['rbr'])
    async def arm_r_bright(self, ctx: commands.Context):
        write_motor(RIGHTARM, BASE, RIGHT, fod(ctx.message.content, 1.0))

    @commands.command(name='rightwristup', aliases=['rwu'])
    async def arm_r_wup(self, ctx: commands.Context):
        write_motor(RIGHTARM, ELBOW, DOWN, fod(ctx.message.content, 1.0))

    @commands.command(name='rightwristdown', aliases=['rwd'])
    async def arm_r_wdown(self, ctx: commands.Context):
        write_motor(RIGHTARM, ELBOW, UP, fod(ctx.message.content, 1.0))

    @commands.command(name='rightelbowup', aliases=['reu'])
    async def arm_r_eup(self, ctx: commands.Context):
        write_motor(RIGHTARM, WRIST, DOWN, fod(ctx.message.content, 1.0))

    @commands.command(name='rightelbowdown', aliases=['red'])
    async def arm_r_edown(self, ctx: commands.Context):
        write_motor(RIGHTARM, WRIST, UP, fod(ctx.message.content, 1.0))

    @commands.command(name='rightshoulderup', aliases=['rsu'])
    async def arm_r_sup(self, ctx: commands.Context):
        write_motor(RIGHTARM, SHOULDER, UP, fod(ctx.message.content, 1.0))

    @commands.command(name='rightshoulderdown', aliases=['rsd'])
    async def arm_r_sdown(self, ctx: commands.Context):
        write_motor(RIGHTARM, SHOULDER, DOWN, fod(ctx.message.content, 1.0))


# Write to the arm device
def write_motor(device, motor, action, time):
    if math.isnan(time):
        time = 1.0
    if time < 0.1:
        time = 0.1
    if arm is not None:
        arm.drive(motor, action, time, device)


def fod(string, default):
    print("Finding numbers in: " + string)
    if any(str.isdigit(c) for c in string):
        numbers = re.findall(r'\d+[.|,]\d+|[.|,]\d|\d\d|\d', string)
        return float(numbers[0])
    return default


def find_usb_devices():
    result = {}
    for file in os.listdir('/sys/bus/usb/drivers/robotic_arm/'):
        if fnmatch.fnmatch(file, '*:*'):
            result[file] = "/sys/bus/usb/drivers/robotic_arm/"+ file + "/"
    return result


arm = Arm(find_usb_devices())


def setup_arms():
    new_keys = []
    for key, value in arm.devices.items():
        print("Setup arm: " + key)
        arm.drive(BASE, RIGHT, 0.5, key)
        arm_name = input("Select arm that moved (l/r):")
        print("Chosen: " + arm_name)
        new_keys.append((key, arm_name))
    arm.remap_names(new_keys)


if __name__ == "__main__":
    setup_arms()
    bot = Bot()
    bot.run()
