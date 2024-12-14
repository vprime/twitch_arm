# bot.py
import math
import os
import re
import fnmatch
from os.path import split

from twitchio.ext import commands, routines
from arm_control import Arm
from chat_log import ChatLog
from enum import Enum

# Arm Device Names
BASE = "basemotor"
GRIP = "gripmotor"
ELBOW = "motor2"
WRIST = "motor3"
SHOULDER = "motor4"
LIGHT = "led"
LEFTARM = "l"
RIGHTARM = "r"

# Device Commands
STOP = "0"
CLOCKWISE = "1"
COUNTER_CLOCKWISE = "2"

UP = CLOCKWISE
DOWN = COUNTER_CLOCKWISE
LEFT = COUNTER_CLOCKWISE
RIGHT = CLOCKWISE
OPEN = COUNTER_CLOCKWISE
CLOSE = CLOCKWISE


# Twitch bot
class Bot(commands.Bot):
    chat_logger = ChatLog()
    def __init__(self):
        super().__init__(
            token=os.environ['TMI_TOKEN'],
            prefix=os.environ['BOT_PREFIX'],
            initial_channels=[os.environ['CHANNEL']],
        )

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        self.reset_arm.start()

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return
        # Print the contents of our message to console...
        print(f'{message.author.name}: {message.content}')
        # Lowercase the messages, so commands can be mixed.
        message.content = message.content.lower()
        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    async def split_arg(self, arg):
        if len(arg) < 3:
            return False
        arm_selected = None
        motor_selected = None
        direction_selected = None
        for i, char in enumerate(arg):
            match i:
                case 0:
                    arm_selected = self.select_arm(char)
                case 1:
                    motor_selected = self.select_motor(char)
                case 2:
                    direction_selected = self.select_direction(char)
        time_selected = fod(arg[3:], 1.0)
        if (arm_selected is not None
                and motor_selected is not None
                and direction_selected is not None
                and time_selected is not None):
            await write_motor(arm_selected, motor_selected, direction_selected, time_selected)
            return True
        return False

    @staticmethod
    def select_arm(value):
        response = None
        match value:
            case "l":
                response = LEFTARM
            case "r":
                response = RIGHTARM
        return response

    @staticmethod
    def select_motor(value):
        response = None
        match value:
            case "g":
                response = GRIP
            case "b":
                response = BASE
            case "w":
                response = WRIST
            case "e":
                response = ELBOW
            case "s":
                response = SHOULDER
        return response

    @staticmethod
    def select_direction(value):
        response = None
        match value:
            case "u":
                response = CLOCKWISE
            case "d":
                response = COUNTER_CLOCKWISE
            case "l":
                response = COUNTER_CLOCKWISE
            case "r":
                response = CLOCKWISE
            case "o":
                response = COUNTER_CLOCKWISE
            case "c":
                response = CLOCKWISE
        return response
    @commands.command(name='chain', aliases=['c', '!'])
    async def chain(self, ctx:commands.Context):
        args = ""
        for arg in ctx.message.content.split():
            if len(arg) < 3:
                continue
            if await self.split_arg(arg):
                args += " " + arg
        if len(args) > 1:
            self.chat_logger.msg(f'{ctx.author.name}:{args}')

    @commands.command(name='leftgripopen', aliases=['lgo'])
    async def arm_l_gopen(self, ctx: commands.Context):
        await write_motor(LEFTARM, GRIP, OPEN, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:lgo')

    @commands.command(name='leftgripclose', aliases=['lgc'])
    async def arm_l_gclose(self, ctx: commands.Context):
        await write_motor(LEFTARM, GRIP, CLOSE, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:lgc')

    @commands.command(name='leftbaseleft', aliases=['lbl'])
    async def arm_l_bleft(self, ctx: commands.Context):
        await write_motor(LEFTARM, BASE, LEFT, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:lbl')

    @commands.command(name='leftbaseright', aliases=['lbr'])
    async def arm_l_bright(self, ctx: commands.Context):
        await write_motor(LEFTARM, BASE, RIGHT, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:lbr')

    @commands.command(name='leftwristup', aliases=['lwu'])
    async def arm_l_wup(self, ctx: commands.Context):
        await write_motor(LEFTARM, WRIST, UP, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:lwu')

    @commands.command(name='leftwristdown', aliases=['lwd'])
    async def arm_l_wdown(self, ctx: commands.Context):
        await write_motor(LEFTARM, WRIST, DOWN, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:lwd')

    @commands.command(name='leftelbowup', aliases=['leu'])
    async def arm_l_eup(self, ctx: commands.Context):
        await write_motor(LEFTARM, ELBOW, UP, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:leu')

    @commands.command(name='leftelbowdown', aliases=['led'])
    async def arm_l_edown(self, ctx: commands.Context):
        await write_motor(LEFTARM, ELBOW, DOWN, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:led')

    @commands.command(name='leftshoulderup', aliases=['lsu'])
    async def arm_l_sup(self, ctx: commands.Context):
        await write_motor(LEFTARM, SHOULDER, UP, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:lsu')

    @commands.command(name='leftshoulderdown', aliases=['lsd'])
    async def arm_l_sdown(self, ctx: commands.Context):
        await write_motor(LEFTARM, SHOULDER, DOWN, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:lsd')

    @commands.command(name='rightgripopen', aliases=['rgo'])
    async def arm_r_gopen(self, ctx: commands.Context):
        await write_motor(RIGHTARM, GRIP, OPEN, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:rgo')

    @commands.command(name='rightgripclose', aliases=['rgc'])
    async def arm_r_gclose(self, ctx: commands.Context):
        await write_motor(RIGHTARM, GRIP, CLOSE, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:rgc')

    @commands.command(name='rightbaseleft', aliases=['rbl'])
    async def arm_r_bleft(self, ctx: commands.Context):
        await write_motor(RIGHTARM, BASE, LEFT, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:rbl')

    @commands.command(name='rightbaseright', aliases=['rbr'])
    async def arm_r_bright(self, ctx: commands.Context):
        await write_motor(RIGHTARM, BASE, RIGHT, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:rbr')

    @commands.command(name='rightwristup', aliases=['rwu'])
    async def arm_r_wup(self, ctx: commands.Context):
        await write_motor(RIGHTARM, WRIST, UP, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:rwu')

    @commands.command(name='rightwristdown', aliases=['rwd'])
    async def arm_r_wdown(self, ctx: commands.Context):
        await write_motor(RIGHTARM, WRIST, DOWN, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:rwd')

    @commands.command(name='rightelbowup', aliases=['reu'])
    async def arm_r_eup(self, ctx: commands.Context):
        await write_motor(RIGHTARM, ELBOW, UP, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:reu')

    @commands.command(name='rightelbowdown', aliases=['red'])
    async def arm_r_edown(self, ctx: commands.Context):
        await write_motor(RIGHTARM, ELBOW, DOWN, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:red')

    @commands.command(name='rightshoulderup', aliases=['rsu'])
    async def arm_r_sup(self, ctx: commands.Context):
        await write_motor(RIGHTARM, SHOULDER, UP, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:rsu')

    @commands.command(name='rightshoulderdown', aliases=['rsd'])
    async def arm_r_sdown(self, ctx: commands.Context):
        await write_motor(RIGHTARM, SHOULDER, DOWN, fod(ctx.message.content, 1.0))
        self.chat_logger.msg(f'{ctx.author.name}:rsd')

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
async def write_motor(device, motor, action, time):
    if math.isnan(time):
        time = 1.0
    if time < 0.1:
        time = 0.1
    if arm is not None:
        arm.drive(motor, action, time, device)

# Float or Default
# Find a number, or return the default
def fod(string, default):
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
