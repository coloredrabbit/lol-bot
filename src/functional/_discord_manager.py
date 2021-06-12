import ssl
import discord
from discord.ext import commands

#다인
import random
import sys
from itertools import combinations

from ..resource.stringconstant import *
from ._discord_channel_manager import getDiscordChannelManager

STR_AVATAR_PATH = "src/resource/icons/64x64.png"
LIMIT_PARTICIPANT_COUNT = 10

app = commands.Bot(command_prefix='!dc')
discordChannelManager = getDiscordChannelManager()

riotApiManager = None


BOT_CLIENT_ID = '809271171786735626'
prefixList = ['<@{}>'.format(BOT_CLIENT_ID), '<@!{}>'.format(BOT_CLIENT_ID)]

def hasPrefix(msg):
    for pre in prefixList:
        if msg.startswith(pre):
            return True
    return False

aliasesList = {
    "info": ['info', '정보'],
    "rot": ['rot', '로테', '로테이션'],
    "show": ['s', '인원', '리스트', '참가자'],
    "add": ['a', '참가', '참여'],
    "rem": ['rm', '삭제', '제외'],
    "reset": ['rs', '초기화', '리셋'],
    "exit": ['종료', '서버종료', '꺼져'],
    "tier": ['티어'],
    "record": ['전적'],
    "banpick": ['ban', '밴픽'],
    "mix_random": ['ran', '랜덤'],
    "mix_balance": ['bal', '밸런스']
}

async def executeCommand(ctx, cmd, text):
    print(cmd)
    print(text)
    if cmd in aliasesList["info"]:
        info(ctx)
    elif cmd in aliasesList["rot"]:
        await rot(ctx)
    elif cmd in aliasesList["show"]:
        await show(ctx)
    elif cmd in aliasesList["add"]:
        await add(ctx, text=text)
    elif cmd in aliasesList["rem"]:
        await rem(ctx, text=text)
    elif cmd in aliasesList["reset"]:
        await reset(ctx, text=text)
    elif cmd in aliasesList["exit"]:
        await exit(ctx)
    elif cmd in aliasesList["tier"]:
        await tier(ctx, text=text)
    elif cmd in aliasesList["record"]:
        await record(ctx, text=text)
    elif cmd in aliasesList["banpick"]:
        await banpick(ctx, text=text)
    elif cmd in aliasesList["mix_random"]:
        await mix_random(ctx)
    elif cmd in aliasesList["mix_balance"]:
        await mix_balance(ctx, text=text)
    else:
        await ctx.send('Invalid command: {}'.format(cmd))

@app.event
async def on_message(message):
    if message.author == app.user:
        return
        
    if hasPrefix(message.content):
        # channel = message.channel
        msgList = message.content.split(None, 2)
        
        if len(msgList) >= 2:
            cmd = msgList[1]
        else:
            cmd = None

        if len(msgList) == 3:
            text = msgList[2]
        else:
            text = ''
        ctx = await app.get_context(message)
        
        if cmd == None:
            await ctx.send('Invalid command: {}'.format(cmd)) # TODO message
        else:
            await executeCommand(ctx, cmd, text)


# general
def discordBotRun(_riotApiManager, discordBotToken):
    #TODO check whether if app already running
    global riotApiManager
    riotApiManager = _riotApiManager

    app.run(discordBotToken)

# message
def _createPlainDiscordMessage(title, fieldName, msg, options = None):
    embed = discord.Embed(title=title)
    embed.add_field(
        name = fieldName
        , value= msg
        , inline = True
    )
    return embed


@app.event
async def on_ready():
    print(app.user.name, 'has connected to Discord!')
    await app.change_presence(status=discord.Status.online, activity=None)
    
    try:
        with open(STR_AVATAR_PATH, 'rb') as avatarFile:
            await app.user.edit(avatar=avatarFile.read())
    except discord.errors.HTTPException:
        # Because you're trying to change avatar too fast. Try later. So ignore this error
        pass

    print("ready")

#TODO
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
        , value= "\r\n".join([riotApiManager._championKey2LocalName[freeCampionId] for freeCampionId in riotApiManager.getChampionRotation()])
        , inline = True
    )
    await ctx.send(embed=embed)

# [civil war]

# show participants
@app.command(aliases=['s', '인원', '리스트', '참가자'])
async def show(ctx):
    participants = discordChannelManager.getParticipants(ctx.channel.id)

    embed = discord.Embed(title=MSG_CURRENT_PARTICIPANTS)
    
    if len(participants) == 0:
        embed.add_field(
            name = 'No participant exists'
            , value = 'No participant exists'
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
@app.command(aliases=aliasesList["add"])
async def add(ctx, *, text):
    participants = discordChannelManager.getParticipants(ctx.channel.id)
    options = discordChannelManager.getOptions(ctx.channel.id)
    print(participants)
    matchEndIndex = options['_bring_match_size']

    addedParticipants = text.split(',')
    if len(participants) + len(addedParticipants) > LIMIT_PARTICIPANT_COUNT:
        await ctx.send(embed=_createPlainDiscordMessage('Error', 'Participant size error', 'Participants cannot exceed to {}'.format(LIMIT_PARTICIPANT_COUNT)))
        return

    invalidSummonerNames = []
    for participant in addedParticipants:
        participant = participant.strip()
        if not participant in participants:
            summonerData = riotApiManager.getSummonerDataByName(participant)
            if summonerData == None:
                invalidSummonerNames.append(participant)
            else:
                seasonData = riotApiManager.getSummonerCurrentSeasonInfoById(summonerData["id"])

                seasonDataAny = seasonData[0]
                if seasonData[0] == None:
                    seasonDataAny = seasonData[1]

                if seasonDataAny != None:
                    summonerData["tier"] = seasonDataAny["tier"]
                    summonerData["rank"] = seasonDataAny["rank"]
                    summonerData["wins"] = seasonDataAny["wins"]
                    summonerData["losses"] = seasonDataAny["losses"]

                summonerData["championMasteries"] = riotApiManager._getChampionMasteries(summonerData["id"])
                summonerData["recentMostChampion"], summonerData["recentMostLane"] = riotApiManager._getRecentMostChampion(summonerData["accountId"], matchEndIndex)
                
                # print(summonerData["championMasteries"]) # !debug
                # print(summonerData["recentMostChampion"]) # !debug
                # print(summonerData["recentMostLane"]) # !debug

                participants[participant] = summonerData

    discordChannelManager.setParticipants(ctx.channel.id, participants)

    if invalidSummonerNames:
        await ctx.send(embed=_createPlainDiscordMessage('Error', 'Invalid sommoners', 'Invalid sommoners: \r\n{}'.format('\r\n'.join(invalidSummonerNames))))
    await show(ctx)

# remove participants
@app.command(aliases=aliasesList["rem"])
async def rem(ctx, *, text):
    participants = discordChannelManager.getParticipants(ctx.channel.id)
    for participant in text.split(','):
        participants.pop(participant.strip(), None)
    discordChannelManager.setParticipants(ctx.channel.id, participants)
    await show(ctx)

@app.command(aliases=aliasesList["reset"])
async def reset(ctx, *, text):
    discordChannelManager.clearChannelData(ctx.channel.id)
    await show(ctx)

@app.command(aliases=aliasesList["exit"])
async def exit(ctx):
    await ctx.send('시스템을 종료합니다') #TODO string resouce
    sys.exit()

@app.command(aliases=aliasesList["tier"])
async def tier(ctx, *, text): # TODO: 인자 하나만 받기
    summonerData = riotApiManager.getSummonerDataByName(text)

    embed = discord.Embed(title="{}'s tier".format(text))
    
    if summonerData == None:
        embed.add_field(name = "No summoner exists", value = text, inline = True)  #TODO: string resource
    else:
        seasonDatas = riotApiManager.getSummonerCurrentSeasonInfo(text)
        seasonTitles = ['Solo', 'Team']
        for index, seasonData in enumerate(seasonDatas):
            message = ''
            if seasonData:
                message = '{} {} : {} win(s) / {} loss(es) - {} pt'.format(
                        seasonData["tier"] # TODO: image resource
                        , seasonData["rank"]
                        , seasonData["wins"]
                        , seasonData["losses"]
                        , seasonData["leaguePoints"]
                    )
            else:
                continue # ignore                
                message = 'Unrank' #TODO: string resource
            embed.add_field(name = seasonTitles[index], value = message, inline = False)
        
        if seasonDatas[0] == None and seasonDatas[1] == None:
            embed.add_field(name = "Unrank", value = "No tier exist", inline = True) #TODO: string resource
        await ctx.send(embed=embed)

@app.command(aliases=aliasesList["record"])
async def record(ctx, *, text): # TODO: 인자 하나만 받기
    summonerData = riotApiManager.getSummonerDataByName(text)
    embed = discord.Embed(title="Recent {}'s matches".format(text))
    
    # field values
    fv_champion          = []
    fv_kill_death_assist = []
    fv_lane              = []

    if summonerData == None:
        await ctx.send(embed=_createPlainDiscordMessage('Error', 'No summoner exists', text)) #TODO: string resource
    else:
        recentMatchList = riotApiManager.getCurrentMatchList(text, 10)
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
                            statKda = 'P'
                        else:
                            statKda = round((statKills + statAssists) / statDeaths, 2)
                        break
                fv_champion.append("{} (Lv. {})".format(riotApiManager._championKey2LocalName[match["champion"]], statChampionLevel))
                fv_kill_death_assist.append("{}/{}/{} ({})".format(statKills, statDeaths, statAssists, statKda))
                fv_lane.append(match["lane"])

                # message += "<:{}:{}>  Lv.{}, {}/{}/{} {}, Lane: {}\r\n".format(
                #         riotApiManager._championKey2LocalName[match["champion"]] #TODO: delete TODO: server emoji <:{}:{}>
                #         , 123 #TODO: emoji id
                #         , statChampionLevel
                #         , statKills
                #         , statDeaths
                #         , statAssists
                #         , statKda
                #         , match["lane"]
                #     )
            embed.add_field(name = 'Champion', value= '\r\n'.join([v for v in fv_champion]), inline = True)
            embed.add_field(name = 'K/D/A',    value= '\r\n'.join([v for v in fv_kill_death_assist]), inline = True)
            embed.add_field(name = 'Lane',     value= '\r\n'.join([v for v in fv_lane]), inline = True)
        else:
            embed.add_field(name = 'No match is recorded', value= 'N/A', inline = True)
        await ctx.send(embed=embed)

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
def recommanedBan(redTeam, blueTeam, participants):
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
            # If you want only one each player in the team
            masteryData = participants[participantName]["championMasteries"][0]
            orderByMastery[index].append((
                riotApiManager._championKey2LocalName[masteryData["championId"]]
                , participantName
                , masteryData["championLevel"]
                , masteryData["championPoints"]
            ))

            # If you want show multiple masteries
            # for masteryData in participants[participantName]["championMasteries"]:
            #     orderByMastery[index].append((
            #         riotApiManager._championKey2LocalName[masteryData["championId"]]
            #         , participantName
            #         , masteryData["championLevel"]
            #         , masteryData["championPoints"]
            #     ))

            for recentMostChampion in participants[participantName]["recentMostChampion"]:
                orderByMostRecentChampion[index].append((riotApiManager._championKey2LocalName[recentMostChampion[0]], participantName, recentMostChampion[1]))

        orderByMastery[index] = sorted(orderByMastery[index], key=lambda x: int(x[2]) * 10000000 + int(x[3]), reverse=True)
        orderByMostRecentChampion[index] = sorted(orderByMostRecentChampion[index], key=lambda x: x[2], reverse=True)

        # Slice. Too many items may exist
        orderByMastery[index] = orderByMastery[index][0:12]
        orderByMostRecentChampion[index] = orderByMostRecentChampion[index][0:12]

    return orderByMastery, orderByMostRecentChampion

'''
!참가 두리쥬와두리, 디다담디담디담, 진희와 재홍이, random135, 되는대로삶, hyuncoo, 동네총각, Dopa PAKA RaIo, 아니 왜 욕을 해요, AeongAeong1
'''

@app.command(aliases=aliasesList["banpick"])
async def banpick(ctx, *, text=''): #TODO delete = ''
    # if(text == ''):
    #     #TODO: error please input team hash code
    #     pass

    # TODO: text = team hashcode
    #redTeam, blueTeam = discordChannelManager.getRecommandedTeam(ctx.channel.id, text)
    redTeam, blueTeam = ['두리쥬와두리', '디다담디담디담', '진희와 재홍이', 'random135', '되는대로삶'], ['hyuncoo', '동네총각', 'Dopa PAKA RaIo', '아니 왜 욕을 해요', 'AeongAeong1']
    # ['두리쥬와두리', '디다담디담디담', '카쥑스매니아', 'random135', '되는대로삶'], ['hyuncoo', '동네총각', 'Dopa PAKA RaIo', '아니 왜 욕을 해요', 'AeongAeong1']
    if redTeam.count == 0 or blueTeam.count == 0:
        # TODO: error on no hash or no exist team
        pass

    orderByMastery, orderByMostRecentChampion = recommanedBan(redTeam, blueTeam, discordChannelManager.getParticipants(ctx.channel.id))

    teamName = ['RED' , 'BLUE']
    tableMasteryHead = ['Champion', 'Participant', 'Level'] #, 'Points']
    tableMostRecentChampionHead = ['Champion', 'Participant', 'Frequency']
    embedColor = [0xf21f18, 0x0067a3]

    for teamIndex, teamItem in enumerate(orderByMastery):
        embed = discord.Embed(title='Recommanded ban pick for {} team'.format(teamName[teamIndex]), color=embedColor[teamIndex])
        embed.add_field(
            name = 'Ban picks for order by mastery'
            , value= '\u200B'
            , inline = False
        )
        
        for index, item in enumerate(tableMasteryHead):
            embed.add_field(
                name = tableMasteryHead[index]
                , value= '\r\n'.join([str(banPickTuple[index]) for banPickTuple in orderByMastery[teamIndex]])
                , inline = True
            )

        # empty horizontal line
        embed.add_field(name = '\u200B' , value= '\u200B', inline = False)

        embed.add_field(
            name = 'Ban picks order by recent most champion'
            , value= '\u200B'
            , inline = False
        )
        for index, item in enumerate(tableMostRecentChampionHead):
            embed.add_field(
                name = tableMostRecentChampionHead[index]
                , value = '\r\n'.join([str(banPickTuple[index]) for banPickTuple in orderByMostRecentChampion[teamIndex]])
                , inline = True
            )
        await ctx.send(embed=embed)

async def _getRecentMatchData(text, matchSize):
    summonerData = riotApiManager.getSummonerDataByName(text)
    recentMatchData = {
        'kill_avg': 0,
        'death_avg': 0,
        'assist_avg': 0,
        'doubleKills': 0,
        'tripleKills': 0,
        'quadraKills': 0,
        'pentaKills': 0,
    }

    if summonerData != None:
        recentMatchList = riotApiManager.getCurrentMatchList(text, matchSize)
        if recentMatchList:
            for match in recentMatchList:
                matchData = riotApiManager._getMatchData(match["gameId"])
                
                inTheMatchTargetParticipantId = -1
                for participantIdentity in matchData["participantIdentities"]:
                    if participantIdentity["player"]["summonerName"] == summonerData["name"]:
                        inTheMatchTargetParticipantId = participantIdentity["participantId"]
                        break

                for participantMatchData in matchData["participants"]:
                    if participantMatchData["participantId"] == inTheMatchTargetParticipantId:
                        recentMatchData['kill_avg'] += participantMatchData["stats"]["kills"]
                        recentMatchData['death_avg'] += participantMatchData["stats"]["deaths"]
                        recentMatchData['assist_avg'] += participantMatchData["stats"]["assists"]                        
                        # statChampionLevel = participantMatchData["stats"]["champLevel"]

                        recentMatchData['doubleKills'] += participantMatchData["stats"]["doubleKills"]
                        recentMatchData['tripleKills'] += participantMatchData["stats"]["tripleKills"]
                        recentMatchData['quadraKills'] += participantMatchData["stats"]["quadraKills"]
                        recentMatchData['pentaKills'] += participantMatchData["stats"]["pentaKills"]
                        # statDoubleKills = participantMatchData["stats"]["doubleKills"]
            if len(recentMatchList) != 0:
                matchLength = len(recentMatchList)
                recentMatchData['kill_avg'] /= matchLength
                recentMatchData['death_avg'] /= matchLength
                recentMatchData['assist_avg'] /= matchLength
    return recentMatchData


output_random_index = 0 # 랜덤 돌리기 횟수
team_group_random = {} # 랜덤으로 빌딩된 팀
num_per_team = 5 # 팀당 인원수
#TODO 김다인: random
@app.command(aliases=aliasesList["mix_random"])
async def mix_random(ctx):
    participants = discordChannelManager.getParticipants(ctx.channel.id)
    
    num_of_participants = int(len(list(participants.keys()))) # 참가자 수

    global output_random_index
    global team_group_random
    global num_per_team

    if not participants: # 참가자가 0명일 때
        await ctx.send('@dc.gg 참가 명령으로 내전에 참가할 인원을 먼저 추가해주세요')
    elif num_of_participants == 1 :
        await ctx.send('랜덤 팀 빌딩 가능 최소인원은 2명입니다. 따라서, @dc.gg 참가 명령으로 참가할 인원을 추가해주세요.')
    else:
        if num_of_participants % 10 == 0 :
            temp_ten = int(num_of_participants / 10)
        elif num_of_participants % 10 != 0 :
            temp_ten = int(num_of_participants / 10 + 1)

        number_of_teams = int(temp_ten * 2) # 팀 개수
        num_per_team = int(num_of_participants / number_of_teams) # 팀당 인원

        randomParticipants = [] 

        # 딕서너리 데이터 형식을 리스트로 변환
        randomParticipants = list(participants.keys())

        number_of_people = len(randomParticipants)
        random.shuffle(randomParticipants) # 팀 랜덤으로 섞기
        
        team_group_random = {}
        red_team_list = [] # redteam list 형태로 저장
        blue_team_list = [] # blueteam list 형태로 저장

        # 팀 분배
        for a in range(0,int(number_of_teams/2)):
            red_team_list.append(randomParticipants[0:num_per_team])
            del randomParticipants[0:num_per_team]
            blue_team_list.append(randomParticipants[0:num_per_team])
            del randomParticipants[0:num_per_team]

        num_of_rest_people = num_of_participants % number_of_teams # 팀 나누고 남은 인원

        for rest in range(0,num_of_rest_people):
            if num_of_rest_people % 2 != 0:
                red_team_list[rest].append(randomParticipants[rest])
            elif num_of_rest_people % 2 == 0:
                blue_team_list[rest-1].append(randomParticipants[rest])

        # if len(blue_team_list[len(blue_team_list)-1]) != len(red_team_list[len(red_team_list)-1]):
        #     blue_team_list[len(blue_team_list)-1].append('김다인')

        team_group_random['red_team'] = red_team_list
        team_group_random['blue_team'] = blue_team_list
    

        
        output_random_index += 1 

        await ctx.send(embed=_getRandomAsString())


def _getRandomAsString():

    embed = discord.Embed(title='랜덤 '+str(output_random_index)+"번째")
    length = len(team_group_random['red_team'])

    for index in range(0,length):
        embed.add_field(
            name = '레드팀'
            , value= '\r\n'.join([name for name in team_group_random['red_team'][index]])
            , inline = True
        )

        embed.add_field(
            name = '블루팀'
            , value= '\r\n'.join([name for name in team_group_random['blue_team'][index]])
            , inline = True
        )

        if length != 1 :
            embed.add_field(
                name = '\u200b'
                , value= '\u200b'
                , inline = False
            )

    return embed


output_balance_index = 0
balance_result = []

#TODO 김다인: balance
@app.command(aliases=aliasesList["mix_balance"])
async def mix_balance(ctx, *, text):
    global output_balance_index
    global balance_result
    global num_per_team
    participants = discordChannelManager.getParticipants(ctx.channel.id)
    num_of_participants = int(len(list(participants.keys())))

    # 밸런스 점수를 위한 데이터, 참가자들명단만 저장
    # 딕서너리 데이터 형식을 리스트로 변환
    balanceParticipantsList = list(participants.keys())
    print(balanceParticipantsList) #!debug

    # TODO 소환사 데이터 예외 처리 >>>
    # if summonerData == None:
    #     embed.add_field(name = "No summoner exists", value = text, inline = True)  #TODO: string resource
    # else:
    #     seasonDatas = riotApiManager.getSummonerCurrentSeasonInfo(text)
    #     print(seasonDatas)

    ########################### <<<
    
    if not participants:
        await ctx.send('@dc.gg 참가 명령으로 내전에 참가할 인원을 먼저 추가해주세요')
    elif num_of_participants != 10:
        await ctx.send('현재는 딱! 10명이어야만 팀 빌딩이 가능합니다')
    else :

        # TODO 점수 >>

        # 시즌 랭킹 점수 데이터
        seasonDatas_element = {}
        for member in balanceParticipantsList:
            seasonDatas_element[member] = riotApiManager.getSummonerCurrentSeasonInfo(member)

        
        # 랭크 데이터 점수 항목 별 값을 담은 딕셔너리
        personal_score_element = {}
        
        for sk,sv in seasonDatas_element.items():
            personal_score_element[sk] = get_score_data_seasonDatas(sv)

        temp_element = {}
        kda_element = {}
 
        for pk,pv in participants.items():
            temp_element = personal_score_element[pk]
            temp_element.update(get_score_data_participantsDatas(pv))
            print(pk) #!debug 범인색출
            temp_element.update(await _getRecentMatchData(pk, 30)) # 최근 30경기
            personal_score_element[pk] = temp_element
        

        # 점수를 담고 있는 딕셔너리
        balanceParticipants = {}

        for k, v in personal_score_element.items():
            balanceParticipants[k] = get_score(v)

        print(balanceParticipants) #!debug
        
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


def get_score_data_seasonDatas(seasonDatas_list):
    score_data = {} # 점수 집계할 데이터만 모음

    # TODO 랭크 데이터가 없을 때
    if seasonDatas_list[0] == None and seasonDatas_list[1] == None:
        score_data['tier'] = 'IRON' # TODO 예외 처리 필요
        score_data['percentage_of_recent_victories'] = 0 # TODO 예외 처리 필요

    # 솔랭 데이터가 없을 때
    elif seasonDatas_list[0] == None:
        score_data['tier'] = seasonDatas_list[1]['tier']
        score_data['percentage_of_recent_victories'] = seasonDatas_list[1]['wins']/(seasonDatas_list[1]['wins']+seasonDatas_list[1]['losses'])

    # 자랭 데이터가 없을 때
    elif seasonDatas_list[1] == None:
        score_data['tier'] = seasonDatas_list[0]['tier']
        score_data['percentage_of_recent_victories'] = seasonDatas_list[0]['wins']/(seasonDatas_list[0]['wins']+seasonDatas_list[0]['losses'])
    
    # TODO 둘 다 있을 때 
    else :
        score_data['tier'] = seasonDatas_list[0]['tier'] # TODO 자랭.. 솔랭...
        score_data['percentage_of_recent_victories'] = (seasonDatas_list[0]['wins']+seasonDatas_list[1]['wins'])/(seasonDatas_list[0]['wins']+seasonDatas_list[0]['losses']+seasonDatas_list[1]['wins']+seasonDatas_list[1]['losses'])
        
    
    return score_data


def get_score_data_participantsDatas(participants_items):
    score_data = {} # 점수 집계할 데이터만 모음

    # TODO 
    if not participants_items :
        return

    score_data['lane'] = participants_items['recentMostLane']
    score_data['number_of_kill'] = 0 # TODO KDA 가져올 API 필요

    return score_data


def get_score(scoreDatas):
    score = {} # 롤 점수 가중치 정의

    score['tier'] = {
        'IRON':1.0,
        'BRONZE':2.0,
        'SILVER':4.0,
        'GOLD':8.0,
        'PLATINUM':15.0,
        'DIAMOND':30.0,
        'MASTER':60,
        'GRAND MASTER':120.0,
        'CHALLENGER':250.0}
    # score['lane']=10.0
    score['percentage_of_victories']=scoreDatas['percentage_of_recent_victories']
    score['number_of_kill']={
        'kill_avg': scoreDatas['kill_avg'] * 20.0, 
        'death_avg':scoreDatas['death_avg'] * -10.0, 
        'assist_avg':scoreDatas['assist_avg'] * 10.0, 
        'doubleKills':scoreDatas['doubleKills']*1.0,
        'tripleKills':scoreDatas['tripleKills']*5.0,
        'quadraKills':scoreDatas['quadraKills']*10.0,
        'pentaKills':scoreDatas['pentaKills']*15.0
    }

    # 최근 20경기 연속킬 횟수 분포 점수
    number_of_kill_score = 0
    for k,v in score['number_of_kill'].items():
        number_of_kill_score += v

    personal_score = float(score['tier'][scoreDatas['tier']]) * 0.4 + float(score['percentage_of_victories'])*0.2+number_of_kill_score*0.2

    return personal_score


    
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
