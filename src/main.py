import ssl
import discord
from discord.ext import commands

from riotwatcher import LolWatcher, ApiError
import pandas as pd

# from functional import dcgg_command

# import sys
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
# import command.py
import requests
def sendHttpRequest(url):
    response = requests.get(url) 
    status = response.status_code 
    return response
# from ./resource import stringconstant


app = commands.Bot(command_prefix='!')
@app.command()
async def echo(ctx, *, text):
    await ctx.send(text)

participants = set()

lolWatcher = LolWatcher(open("./riotApiKey.txt", "r").readline())
lolWatcherRegion = 'kr' #default value: kr
validRegions = ['BR1', 'EUN1', 'EUW1', 'JP1', 'KR', 'LA1', 'LA2', 'NA1', 'OC1', 'TR1', 'RU']

@app.command()
async def local(ctx, *, text):
    for validRegion in validRegions:
        if(validRegion.lower == text):
            lolWatcherRegion = text
            await ctx.send(text + 'region setting success')
    await ctx.send(text)

@app.command()
async def add(ctx, *, text):
    for participant in text.split(','):

        participants.add(participants)
    result = ', '.join(participants)
    await ctx.send(result)
@app.command()
async def 참가(ctx, *, text):
    await add(ctx, *, text)

@app.command()
async def rot(ctx, *, text):
    #res = sendHttpRequest('/lol/platform/v3/champion-rotations')
    await ctx.send(text)


@app.event
async def on_ready():
    print(app.user.name, 'has connected to Discord!')
    await app.change_presence(status=discord.Status.online, activity=None)
    print("ready")

app.run(open("./key.txt", "r").readline())