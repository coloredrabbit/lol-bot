import ssl
import discord
from discord.ext import commands

#다인
import random
import sys
from itertools import combinations

from resource.stringconstant import *
from functional._discord_channel_manager import getDiscordChannelManager

app = commands.Bot(command_prefix='!')
discordChannelManager = getDiscordChannelManager()

riotApiManager = None
imageManager = None

# general
def discordBotRun(_riotApiManager, _imageManager, discordBotToken):
    #TODO check whether if app already running
    global riotApiManager
    riotApiManager = _riotApiManager

    global imageManager
    imageManager = _imageManager

    app.run(discordBotToken)

# message
def _createDiscordMessage(msg, options = None):
    return "```{}```".format(msg)

@app.event
async def on_ready():
    print(app.user.name, 'has connected to Discord!')
    await app.change_presence(status=discord.Status.online, activity=None)
    print("ready")

@app.command(aliases=['정보'])
async def info(ctx):
    await ctx.send()

#commands
@app.command()
async def echo(ctx, *, text):
    await ctx.send(text)

@app.command(aliases=['로테', '로테이션'])
async def rot(ctx):
    embed = discord.Embed(title=MSG_SHOW_ROTATION)
    embed.add_field(
        name = MSG_FREE_CHAMPION
        , value= join([riotApiManager._championKey2LocalName[freeCampionId] for freeCampionId in riotApiManager.getChampionRotation()])
        , inline = True
    )
    await ctx.send(embed=embed)

@app.command(aliases=['tier', '티어', '그님티'])
async def rem(ctx, *, text):
    
    await show(ctx)

# [civil war]

# show participants
@app.command(aliases=['s', '인원', '리스트', '참가자'])
async def show(ctx):
    participants = discordChannelManager.getParticipants(ctx.channel.id)

    embed = discord.Embed(title=MSG_CURRENT_PARTICIPANTS)
    
    if participants.count == 0:
        embed.add_field(
            name = 'No participant exists'
            , inline = True
        )
    else :
        embed.add_field(
            name = 'Name'
            , value= '\r\n'.join([name for name in participants])
            , inline = True
        )
        embed.add_field(
            name = 'Highest mastery'
            , value= '\r\n'.join([riotApiManager._championKey2LocalName[participants[name]["championMasteries"][0]['championId']] for name in participants])
            , inline = True
        )
        embed.add_field(
            name = 'Recent most pick'
            , value= '\r\n'.join([riotApiManager._championKey2LocalName[participants[name]["recentMostChampion"][0][0]] for name in participants])
            , inline = True
        )
        embed.add_field(
            name = 'Recent most lane'
            , value= '\r\n'.join([participants[name]["recentMostLane"][0][0] for name in participants])
            , inline = True
        )
    await ctx.send(embed=embed)

# add participants
@app.command(aliases=['a', '참가', '참여'])
async def add(ctx, *, text):
    participants = discordChannelManager.getParticipants(ctx.channel.id)
    options = discordChannelManager.getOptions(ctx.channel.id)

    matchEndIndex = options['_bring_match_size']

    invalidSummonerNames = []
    for participant in text.split(','):
        participant = participant.strip()
        if not participant in participants:
            summonerData = riotApiManager.getSummonerDataByName(participant)
            if summonerData == None:
                invalidSummonerNames.append(participant)
            else:
                seasonData = riotApiManager.getSummonerCurrentSeasonInfoById(summonerData["id"])

                if seasonData != None:
                    summonerData["tier"] = seasonData["tier"]
                    summonerData["rank"] = seasonData["rank"]
                    summonerData["wins"] = seasonData["wins"]
                    summonerData["losses"] = seasonData["losses"]

                summonerData["championMasteries"] = riotApiManager._getChampionMasteries(summonerData["id"])
                summonerData["recentMostChampion"], summonerData["recentMostLane"] = riotApiManager._getRecentMostChampion(summonerData["accountId"], matchEndIndex)
                
                # print(summonerData["championMasteries"]) # !debug
                # print(summonerData["recentMostChampion"]) # !debug
                # print(summonerData["recentMostLane"]) # !debug

                participants[participant] = summonerData

    discordChannelManager.setParticipants(ctx.channel.id, participants)

    if invalidSummonerNames:
        await ctx.send(_createDiscordMessage('Invalid sommoners: \r\n{}'.format('\r\n'.join(invalidSummonerNames))))
    await show(ctx)

# remove participants
@app.command(aliases=['rm', '삭제', '제외'])
async def rem(ctx, *, text):
    participants = discordChannelManager.getParticipants(ctx.channel.id)
    for participant in text.split(','):
        participants.pop(participant.strip(), None)
    discordChannelManager.setParticipants(ctx.channel.id, participants)
    await show(ctx)

@app.command(aliases=['rs', '초기화', '리셋'])
async def reset(ctx, *, text):
    discordChannelManager.clearChannelData(ctx.channel.id)
    await show('```All remanined data in server have been removed```')

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
                        , riotApiManager._championKey2LocalName[match["champion"]]
                        , statChampionLevel                        
                        , statKills
                        , statDeaths
                        , statAssists
                        , statKda
                    )
        else:
            message = 'No match is recorded' #TODO: string resource
        await ctx.send(_createDiscordMessage(message))

'''
Each lane, ban pick supplied upto 5 picks

[INPUT]
redTeam = ['participant1Name', 'participant2Name', ...]
blueTeam = ['participant1Name', 'participant2Name', ...]

[OUTPUT]
banPickForRedTeam = [
    {
        "participantName": "",
        "championId": 0,
        "mastery": 0
    }
]
banPickForBlueTeam = [...]
'''
def recommanedBan(redTeam, blueTeam):
    # if not participants:
    #     await ctx.send('!참가 명령으로 내전에 참가할 인원을 먼저 추가해주세요')
    #     pass
    
    # # TODO check validation running ban algorithm
    # if False:
    #     await ctx.send('인원수 부족 또는 다른 유효성 검사')
    #     pass

    if redTeam.count != 5 or blueTeam.count != 5:
        # TODO: error
        pass

    teams = [redTeam, blueTeam]
    orderByMastery = [[], []]
    orderByMostRecentChampion = [[], []]
    for index, item in enumerate(orderByMastery):
        for participantName in teams[(index+1)%2]:
            for masteryData in participants[participantName]["championMasteries"]:
                orderByMastery[index].append((
                    riotApiManager._championKey2Name[masteryData["championId"]]
                    , participantName
                    , masteryData["championLevel"]
                    , masteryData["championPoints"]
                ))

            for recentMostChampion in participants[participantName]["recentMostChampion"]:
                orderByMostRecentChampion[index].append((riotApiManager._championKey2Name[recentMostChampion[0]], participantName, recentMostChampion[1]))

        orderByMastery[index] = sorted(orderByMastery[index], key=lambda x: x[2], reverse=True)
        orderByMostRecentChampion[index] = sorted(orderByMostRecentChampion[index], key=lambda x: x[2], reverse=True)

        # Slice. Too many items may exist
        orderByMastery[index] = orderByMastery[index][0:12]
        orderByMostRecentChampion[index] = orderByMostRecentChampion[index][0:12]

    return orderByMastery, orderByMostRecentChampion

@app.command(name='밴픽')
async def testBan(ctx, *, text = ''):
    if(text == ''):
        #TODO: error please input team hash code
        pass
    # TODO: text = team hashcode
    redTeam, blueTeam = discordChannelManager.getRecommandedTeam(ctx.channel.id, text)
    # ['두리쥬와두리', '디다담디담디담', '카쥑스매니아', 'random135', '되는대로삶'], ['hyuncoo', '동네총각', 'Dopa PAKA RaIo', '아니 왜 욕을 해요', 'AeongAeong1']
    if redTeam.count == 0 or blueTeam.count == 0:
        # TODO: error on no hash or no exist team
        pass

    orderByMastery, orderByMostRecentChampion = recommanedBan(redTeam, blueTeam)

    teamName = ['red' , 'blue']
    tableMasteryHead = ['Champion', 'Participant', 'Level', 'Points']
    tableMostRecentChampionHead = ['Champion', 'Participant', 'Frequency']
    for teamIndex, teamItem in enumerate(orderByMastery):
        masteryEmbed = discord.Embed(title='Ban picks for {} team order by mastery'.format(teamName[teamIndex]))
        
        for index, item in enumerate(tableMasteryHead):
            masteryEmbed.add_field(
                name = tableMasteryHead[index]
                , value= '\r\n'.join([str(banPickTuple[index]) for banPickTuple in orderByMastery[teamIndex]])
                , inline = True
            )
        await ctx.send(embed=masteryEmbed)

        recentMostChampionEmbed = discord.Embed(title='Ban picks for {} team order by recent most champion'.format(teamName[teamIndex]))
        for index, item in enumerate(tableMostRecentChampionHead):
            recentMostChampionEmbed.add_field(
                name = tableMostRecentChampionHead[index]
                , value= '\r\n'.join([str(banPickTuple[index]) for banPickTuple in orderByMostRecentChampion[teamIndex]])
                , inline = True
            )
        await ctx.send(embed=recentMostChampionEmbed)
    
    
'''
!참가 두리쥬와두리, 디다담디담디담, 카쥑스매니아, random135, 되는대로삶, hyuncoo, 동네총각, Dopa PAKA RaIo, 아니 왜 욕을 해요, AeongAeong1
'''

output_random_index = 0
team_group_random = {}
num_per_team = 5
#TODO 김다인: random
@app.command(name='랜덤')
async def mix_random(ctx, *, text):
    participants = _getParticipants(ctx.channel.id)
    
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
    participants = _getParticipants(ctx.channel.id)

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
