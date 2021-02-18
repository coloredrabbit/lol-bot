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
    embed = discord.Embed(title=MSG_CURRENT_PARTICIPANTS)
    embed.add_field(
        name = 'Name'
        , value= '\r\n'.join([name for name in participants])
        , inline = True
    )
    embed.add_field(
        name = 'Highest mastery'
        , value= '\r\n'.join([riotApiManager._championKey2Name[participants[name]["championMasteries"][0]['championId']] for name in participants])
        , inline = True
    )
    embed.add_field(
        name = 'Recent most pick'
        , value= '\r\n'.join([riotApiManager._championKey2Name[participants[name]["recentMostChampion"][0][0]] for name in participants])
        , inline = True
    )
    embed.add_field(
        name = 'Recent most lane'
        , value= '\r\n'.join([participants[name]["recentMostLane"][0][0] for name in participants])
        , inline = True
    )

    # embed.set_footer(text=ctx.author.name, icon_url = ctx.author.avatar_url)

    return embed

# show participants
@app.command(aliases=['s', '인원', '리스트', '참가자'])
async def show(ctx):
    await ctx.send(embed=_getParticipantsAsString())

# add participants
@app.command(aliases=['a', '참가', '참여'])
async def add(ctx, *, text):
    invalidSummonerNames = []
    for participant in text.split(','):
        participant = participant.strip()
        if not participant in participants:
            summonerData = riotApiManager.getSummonerDataByName(participant)
            if summonerData == None:
                invalidSummonerNames.append(participant)
            else:
                seasonData = riotApiManager.getSummonerCurrentSeasonInfoById(summonerData["id"])
                print(seasonData) # !debug
                if seasonData != None:
                    summonerData["tier"] = seasonData["tier"]
                    summonerData["rank"] = seasonData["rank"]
                    summonerData["wins"] = seasonData["wins"]
                    summonerData["losses"] = seasonData["losses"]

                summonerData["championMasteries"] = riotApiManager._getChampionMasteries(summonerData["id"])
                summonerData["recentMostChampion"], summonerData["recentMostLane"] = riotApiManager._getRecentMostChampion(summonerData["accountId"])
                
                print(summonerData["championMasteries"]) # !debug
                print(summonerData["recentMostChampion"]) # !debug
                print(summonerData["recentMostLane"]) # !debug

                participants[participant] = summonerData

    if invalidSummonerNames:
        await ctx.send(_createDiscordMessage('Invalid sommoners: \r\n{}'.format('\r\n'.join(invalidSummonerNames))))
    await show(ctx)

# remove participants
@app.command(aliases=['rm', '삭제', '제외'])
async def rem(ctx, *, text):
    for participant in text.split(','):
        participants.pop(participant.strip(), None)
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
        await ctx.send('No summoner exists: {}'.format(text)) #TODO: string resource
    else:
        seasonData = riotApiManager.getSummonerCurrentSeasonInfo(text)
        message = ''
        if seasonData:
            message = '{} {} : {} win(s) / {} loss(es) - {} pt'.format(
                    seasonData["tier"]
                    , seasonData["rank"]
                    , seasonData["wins"]
                    , seasonData["losses"]
                    , seasonData["leaguePoints"]
                )
        else:
            message = 'Unrank' #TODO: string resource
        await ctx.send(_createDiscordMessage(message))

@app.command(aliases=['전적'])
async def record(ctx, *, text): # TODO: 인자 하나만 받기
    summonerData = riotApiManager.getSummonerDataByName(text)
    if summonerData == None:
        await ctx.send('No summoner exists: {}'.format(text)) #TODO: string resource
    else:
        recentMatchList = riotApiManager.getCurrentMatchList(text)
        message = ''
        if recentMatchList:
            for match in recentMatchList:
                matchData = riotApiManager._getMatchData(match["gameId"])
                statKills = 0
                statDeaths = 0
                statAssists = 0
                statKda = 0
                statChampionLevel = 0

                inTheMatchTargetParticipantId = -1
                for participantIdentity in matchData["participantIdentities"]:
                    if participantIdentity["player"]["summonerName"] == summonerData["name"]:
                        inTheMatchTargetParticipantId = participantIdentity["participantId"]
                        break

                for participantMatchData in matchData["participants"]:
                    if participantMatchData["participantId"] == inTheMatchTargetParticipantId:
                        statKills = participantMatchData["stats"]["kills"]
                        statDeaths = participantMatchData["stats"]["deaths"]
                        statAssists = participantMatchData["stats"]["assists"]                        
                        statChampionLevel = participantMatchData["stats"]["champLevel"]

                        if statDeaths == 0:
                            statKda = 'Perfect'
                        else:
                            statKda = (statKills + statAssists) / statDeaths
                        break
                message += "Lane: {}, Champion: {} {}, {}/{}/{} {}\r\n".format(
                        match["lane"]
                        , riotApiManager._championKey2Name[match["champion"]]
                        , statChampionLevel                        
                        , statKills
                        , statDeaths
                        , statAssists
                        , statKda
                    )
        else:
            message = 'No match is recorded' #TODO: string resource
        await ctx.send(_createDiscordMessage(message))

def recommanedBan(redTeam, blueTeam):
    # if not participants:
    #     await ctx.send('!참가 명령으로 내전에 참가할 인원을 먼저 추가해주세요')
    #     pass
    
    # # TODO check validation running ban algorithm
    # if False:
    #     await ctx.send('인원수 부족 또는 다른 유효성 검사')
    #     pass
    

    return [], []
    
#TODO 김다인: random
@app.command(name='랜덤')
async def mix_random(ctx, *, text):
    if not participants:
        await ctx.send('!참가 명령으로 내전에 참가할 인원을 먼저 추가해주세요')

    else :
        randomParticipants = [] 

        # 딕서너리 데이터 형식을 리스트로 변환
        for k, v in participant.items():
            randomParticipants.append(k)
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