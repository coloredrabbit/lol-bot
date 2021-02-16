import ssl
import discord
from discord.ext import commands

#다인
import random
import sys

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
async def mix_random(ctx, *, text):
    # 서버 끄기
    if text == '종료':
        await ctx.send('시스템을 종료합니다')
        sys.exit()
    
    if not participants:
        await ctx.send('!참가 명령으로 내전에 참가할 인원을 먼저 추가해주세요')

    else :

        randomParticipants = list(participants)
        number_of_people = len(randomParticipants)
        number_of_teams = int(number_of_people / 5) # 팀 개수

        random.shuffle(randomParticipants) # 팀 랜덤으로 섞기
        number_of_rest = int(number_of_people % 5) # 팀 나누고 나머지 인원
        team_group = [] # 랜덤 팀

        for i in range(0,number_of_teams):
            team_group.append(randomParticipants[0:5])
            del randomParticipants[0:5]
        
        # 팀이 나누어 떨어지지 않을 때
        if number_of_rest != 0:
            team_group.append(randomParticipants[0:number_of_rest])

        await ctx.send(team_group)

@app.command()
async def 랜덤(ctx, *, text):
    await mix_random(**locals())