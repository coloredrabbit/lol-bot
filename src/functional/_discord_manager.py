import ssl
import discord
from discord.ext import commands

from resource.stringconstant import *

app = commands.Bot(command_prefix='!')

# general
def discordBotRun(discordBotToken):
    #TODO check whether if app already running
    app.run(discordBotToken)

# message
def _createDiscordMessage(msg, options = None):
    return "```{}```".format(msg)

@app.event
async def on_ready():
    print(app.user.name, 'has connected to Discord!')
    await app.change_presence(status=discord.Status.online, activity=None)
    print("ready")

#commands
@app.command()
async def echo(ctx, *, text):
    await ctx.send(text)

@app.command()
async def local(ctx, *, text):
    for validRegion in validRegions:
        if(validRegion.lower == text):
            lolWatcherRegion = text
            await ctx.send(text + 'region setting success')
    await ctx.send(text)


@app.command()
async def rot(ctx, *, text):
    #TODO use riotApiManager
    #res = sendHttpRequest('/lol/platform/v3/champion-rotations')
    await ctx.send(text)

# [civil war]
participants = set()

#TODO get participants by application id
def _getParticipants():
    return participants

def _getParticipantsAsString():
    return _createDiscordMessage(MSG_CURRENT_PARTICIPANTS.format('\r\n'.join(participants)))

# show participants
@app.command(aliases=['s', '인원', '리스트', '참가자'])
async def show(ctx):
    await ctx.send(_getParticipantsAsString())

# add participants
@app.command(aliases=['a', '참가', '참여'])
async def add(ctx, *, text):
    for participant in text.split(','): 
        participants.add(participant)
    await _show(ctx)

# remove participants
@app.command(aliases=['rm', '삭제', '제외'])
async def rem(ctx, *, text):
    for participant in text.split(','):
        participants.discard(participant)
    await _show(ctx)

@app.command(aliases=['rs', '초기화', '리셋'])
async def reset(ctx, *, text):
    participants.clear()
    await _show(ctx)

#TODO 김다인: random
@app.command(name='랜덤')
async def random(ctx, *, text):
    pass