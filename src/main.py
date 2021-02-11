import ssl
import discord
from discord.ext import commands

app = commands.Bot(command_prefix='!')


@app.event
async def on_ready():
    print(app.user.name, 'has connected to Discord!')
    await app.change_presence(status=discord.Status.online, activity=None)
    print("ready")

@app.command()
async def testCommand(ctx, *, text):
    await ctx.send(text)

app.run(open("./key.txt", "r").readline())