import ssl
import discord
from discord.ext import commands

app = commands.Bot(command_prefix='!')
participants = set()

def discordBotRun(discordBotToken):
    #TODO check whether if app already running
    app.run(discordBotToken)

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
# add participants
@app.command()
async def add(ctx, *, text):
    for participant in text.split(','):        
        participants.add(participant)
    await ctx.send(', '.join(participants))

@app.command()
async def 참가(ctx, *, text):
    await add(**locals())

# remove participants
@app.command()
async def rem(ctx, *, text):
    for participant in text.split(','):        
        participants.discard(participant)
    await ctx.send(', '.join(participants))

@app.command()
async def 삭제(ctx, *, text):
    await rem(**locals())

#TODO 김다인: random
@app.command()
async def random(ctx, *, text):
    pass

@app.command()
async def 랜덤(ctx, *, text):
    await random(**locals())