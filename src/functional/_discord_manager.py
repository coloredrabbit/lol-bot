import ssl
import discord
from discord.ext import commands

#다인
import random
import sys
from itertools import combinations

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

output_random_index = 0
team_group_random = {}
num_per_team = 5
#TODO 김다인: random
@app.command(name='랜덤')
async def mix_random(ctx, *, text):

    num_of_participants = int(len(list(participants.keys())))

    if not participants:
        await ctx.send('!참가 명령으로 내전에 참가할 인원을 먼저 추가해주세요')
    elif num_of_participants != 10:
        await ctx.send('현재는 딱! 10명이어야만 팀 빌딩이 가능합니다')
    else :
        global output_random_index
        global team_group_random
        global num_per_team

        randomParticipants = [] 

        # 딕서너리 데이터 형식을 리스트로 변환
        randomParticipants = list(participants.keys())

        number_of_people = len(randomParticipants)
        number_of_teams = int(number_of_people / num_per_team) # 팀 개수

        random.shuffle(randomParticipants) # 팀 랜덤으로 섞기
        number_of_rest = int(number_of_people % num_per_team) # 팀 나누고 나머지 인원
        
        team_group_random = {}

        # for red in range(0,number_of_teams):
        team_group_random['red_team'] = randomParticipants[0:num_per_team]
        del randomParticipants[0:num_per_team]
        team_group_random['blue_team'] = randomParticipants[0:num_per_team]
        
        # 팀이 나누어 떨어지지 않을 때
        # if number_of_rest != 0:
        #     team_group_random['blue_team'] = randomParticipants[0:number_of_rest]

        output_random_index += 1

        await ctx.send(embed=_getRandomAsString())


def _getRandomAsString():

    embed = discord.Embed(title='랜덤 '+str(output_random_index)+"번째")
    embed.add_field(
        name = '레드팀'
        , value= '\r\n'.join([name for name in team_group_random['red_team']])
        , inline = True
    )
    
    embed.add_field(
        name = '블루팀'
        , value= '\r\n'.join([name for name in team_group_random['blue_team']])
        , inline = True
    )

    return embed


output_balance_index = 0
balance_result = []

#TODO 김다인: balance
@app.command(name='밸런스')
async def mix_balance(ctx, *, text):
    global output_balance_index
    global balance_result
    global num_per_team

    num_of_participants = int(len(list(participants.keys())))

    if not participants:
        await ctx.send('!참가 명령으로 내전에 참가할 인원을 먼저 추가해주세요')
    elif num_of_participants != 10:
        await ctx.send('현재는 딱! 10명이어야만 팀 빌딩이 가능합니다')
    else :
        # 필요한 정보만 담긴 딕셔너리로 변환
        balanceParticipants = {}
        for k, v in participants.items():
            balanceParticipants[k] = v['profileIconId'] # TODO 점수

        index = 0
        team_combinations = [] # 팀 조합으로 소환사명만 들어있는 list

        # 팀 조합 (Combination)
        for team in combinations(balanceParticipants,num_per_team):
            team_combinations.append(team) 

        # 팀 블루, 레드로 매칭
        length = len(team_combinations)
        num = int(length/2)
        team_red_all = [] # 레드팀 목록
        team_blue_all = [] # 블루팀 목록
        for x in range(0,num):
            team_red_all.append(team_combinations[x])
            team_blue_all.append(team_combinations[length-1-x])

        team_group_balance = [] # 밸런스 팀 및 점수
        for i in range(0,num):
            team_group_element = {}
            team_group_element['red_team'] = team_red_all[i] # 팀 레드
            team_group_element['blue_team'] = team_blue_all[i] # 팀 블루

            # 점수 차이 계산
            # 레드팀 점수
            red_score = 0
            red_score_avg = 1
            for person_red in team_red_all[i]:
                red_score += balanceParticipants[person_red]
            red_score_avg = red_score / len(team_red_all[i])

            # 블루팀 점수
            blue_score = 0
            blue_score_avg = 1
            for person_blue in team_blue_all[i]:
                blue_score += balanceParticipants[person_blue]
            blue_score_avg = blue_score / len(team_blue_all[i])

            avg_score = red_score_avg - blue_score_avg # 점수 차이
            if avg_score < 0:
                avg_score *= -1

            team_group_element['diff'] = avg_score

            team_group_balance.append(team_group_element)

        balance_result = sorted(team_group_balance, key = lambda team_group_balance : team_group_balance['diff'])

        if output_balance_index >= len(balance_result):
            output_balance_index = 0

        await ctx.send(embed=_getBalanceAsString())

    
def _getBalanceAsString():
    global output_balance_index
    global balance_result

    embed = discord.Embed(title='밸런스 '+str(output_balance_index+1)+"번째")
    embed.add_field(
        name = '레드팀'
        , value= '\r\n'.join([name for name in balance_result[output_balance_index]['red_team']])
        , inline = True
    )
    
    embed.add_field(
        name = '블루팀'
        , value= '\r\n'.join([name for name in balance_result[output_balance_index]['blue_team']])
        , inline = True
    )

    output_balance_index += 1

    return embed
