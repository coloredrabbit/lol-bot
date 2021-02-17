import ssl
import discord
from discord.ext import commands

#다인
import random
import sys

from resource.stringconstant import *

app = commands.Bot(command_prefix='!')

riotApiManager = None
# general
def discordBotRun(_riotApiManager, discordBotToken):
    #TODO check whether if app already running
    global riotApiManager
    riotApiManager = _riotApiManager
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

@app.command(aliases=['로테', '로테이션'])
async def rot(ctx):
    message = '\r\n'.join(riotApiManager.getChampionRotation())

    await ctx.send(message)

# [civil war]
'''
participants = {
    "{summonerName}": {
        "id": "",
        "accountId": "",
        "puuid": "",
        "name": "{summonerName}",
        "profileIconId": Integer,
        "revisionDate": Integer,
        "summonerLevel": Integer
    },
    ...
}
'''
participants = {}

#TODO get participants by application id
def _getParticipants():
    return participants

def _getParticipantsAsString():
    return _createDiscordMessage(MSG_CURRENT_PARTICIPANTS.format('\r\n'.join([name for name in participants])))

# show participants
@app.command(aliases=['s', '인원', '리스트', '참가자'])
async def show(ctx):
    await ctx.send(_getParticipantsAsString())

# add participants
@app.command(aliases=['a', '참가', '참여'])
async def add(ctx, *, text):
    invalidSummonerNames = []
    for participant in text.split(','):
        summonerData = riotApiManager.getSummonerDataByName(participant)
        if summonerData == None:
            invalidSummonerNames.append(participant)
        else:
            seasonData = riotApiManager.getSummonerCurrentSeasonInfoById(summonerData["id"])
            summonerData["tier"] = seasonData["tier"]
            summonerData["rank"] = seasonData["rank"]
            summonerData["wins"] = seasonData["wins"]
            summonerData["loses"] = seasonData["loses"]

            participants[participant] = summonerData
    if invalidSummonerNames:
        await ctx.send(_createDiscordMessage('Invalid sommoners: \r\n{}'.format('\r\n'.join(invalidSummonerNames))))
    await show(ctx)

# remove participants
@app.command(aliases=['rm', '삭제', '제외'])
async def rem(ctx, *, text):
    for participant in text.split(','):
        participants.pop(participant, None)
    await show(ctx)

@app.command(aliases=['rs', '초기화', '리셋'])
async def reset(ctx, *, text):
    participants.clear()
    await show(ctx)

@app.command(aliases=['종료', '서버종료', '꺼져'])
async def exit(ctx):
    await ctx.send('시스템을 종료합니다') #TODO string resouce
    sys.exit()

@app.command(aliases=['티어'])
async def tier(ctx, *, text): # TODO: 인자 하나만 받기
    summonerData = riotApiManager.getSummonerDataByName(text)
    if summonerData == None:
        await ctx.send('No summoner exists: {}', text) #TODO: string resource
    else:
        seasonData = riotApiManager.getSummonerCurrentSeasonInfo(text)
        message = ''
        if seasonData:
            message = '{} {} : {} win(s) / {} loss(es) - {} pt'.format(seasonData["tier"], seasonData["rank"], seasonData["wins"], seasonData["losses"], seasonData["leaguePoints"])
        else:
            message = 'Unrank' #TODO: string resource
        await ctx.send(_createDiscordMessage(message))

#TODO 김다인: random
@app.command(name='랜덤')
async def mix_random(ctx, *, text):
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