# bot.py
import os, re
from twitchio.ext import commands
from pprint import pprint
from arm_control import Arm
from tts_control import setup_speak, speak

# Arm Device Names
BASE = "basemotor"
GRIP = "gripmotor"
WRIST = "motor2"
ELBOW = "motor3"
SHOULDER = "motor4"
LIGHT = "led"
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


bot = commands.Bot(
    # set up the bot
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[os.environ['CHANNEL']]
)
#setup_speak()

@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f"{os.environ['BOT_NICK']} is online!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(os.environ['CHANNEL'], f"/me is online!")


@bot.event
async def event_message(ctx):
    'Runs every time a message is sent in chat.'
    #speak(ctx.content)
    await bot.handle_commands(ctx)
    # make sure the bot ignores itself and the streamer
    if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
        return


arm = Arm()

@bot.command(name='gripopen', aliases=['go'])
async def arm_gopen(ctx):
    write_motor(GRIP, OPEN, fod(ctx.content, 1.0))

@bot.command(name='gripclose', aliases=['gc'])
async def arm_gclose(ctx):
    write_motor(GRIP, CLOSE, fod(ctx.content, 1.0))
    
@bot.command(name='baseleft', aliases=['bl'])
async def arm_bleft(ctx):
    write_motor(BASE, LEFT, fod(ctx.content, 1.0))
    
@bot.command(name='baseright', aliases=['br'])
async def arm_bright(ctx):
    write_motor(BASE, RIGHT, fod(ctx.content, 1.0))
    
@bot.command(name='wristup', aliases=['wu'])
async def arm_wup(ctx):
    write_motor(WRIST, UP, fod(ctx.content, 1.0))
    
@bot.command(name='wristdown', aliases=['wd'])
async def arm_wdown(ctx):
    write_motor(WRIST, DOWN, fod(ctx.content, 1.0))
    
@bot.command(name='elbowup', aliases=['eu'])
async def arm_eup(ctx):
    write_motor(ELBOW, UP, fod(ctx.content, 1.0))
    
@bot.command(name='elbowdown', aliases=['ed'])
async def arm_edown(ctx):
    write_motor(ELBOW, DOWN, fod(ctx.content, 1.0))
    
@bot.command(name='shoulderup', aliases=['su'])
async def arm_sup(ctx):
    write_motor(SHOULDER, UP, fod(ctx.content, 1.0))
    
@bot.command(name='shoulderdown', aliases=['sd'])
async def arm_sdown(ctx):
    write_motor(SHOULDER, DOWN, fod(ctx.content, 1.0))



# Write to the arm device
def write_motor(motor, action, time):
    arm.drive(motor, action, time)

def fod(string, default):
    if(any(str.isdigit(c) for c in string)):
        numbers = re.findall("\d+\.\d+|\.\d|\d\d|\d", string)
        return float(numbers[0])
    return default


if __name__ == "__main__":
    bot.run()
