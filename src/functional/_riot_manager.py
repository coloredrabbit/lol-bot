import requests
import json
import os
import codecs
import urllib

from collections import defaultdict

from resource.stringconstant import *

#TODO
def _riotApiManagerGenerator(riotApiKey):
    # 1. Region
    # 2. Riot API version
    # 3. Rest API path
    # 4. Riot API key
    RIOT_REST_API_FORMAT = "https://{}.api.riotgames.com{}?api_key={}"


    # 1. Riot LOL release version
    # 2. region
    RIOT_DDRAGON_CHAMPION_JSON = 'http://ddragon.leagueoflegends.com/cdn/{}/data/{}/champion.json'
    RIOT_DDRAGON_CHAMPION_JSON_FILE_CACHE_PATH = './src/resource/_cache/{}_{}.json'

    RIOT_DDRAGON_CHAMPION_SQUARE_ASSETS = 'http://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}.png'

    class _riotApiManager:
        lolReleaseVersion = '11.3.1'

        # Riot API
        validRiotApiRegions = ['BR1', 'EUN1', 'EUW1', 'JP1', 'KR', 'LA1', 'LA2', 'NA1', 'OC1', 'TR1', 'RU']
        riotApiRegion = 'kr' #default value: kr

        # ddragon API
        # ddragon region: language[_territory] see https://en.wikipedia.org/wiki/Locale_(computer_software), https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
        validDdrationApiRegions = ['ko_KR', 'en_US']
        ddragonApiLocale = 'ko_KR' #default value: ko_KR

        def __init__(self, riotApiKey):
            self.riotApiKey = riotApiKey
            self._loadChampionData()
            
        def _loadChampionData(self):
            # load champion data
            championCacheJsonFilePath = RIOT_DDRAGON_CHAMPION_JSON_FILE_CACHE_PATH.format(self.lolReleaseVersion, self.ddragonApiLocale)
            if os.path.exists(championCacheJsonFilePath):
                print('already exist riot champion data')
                self.champion = json.load(codecs.open(championCacheJsonFilePath, 'r', "utf-8-sig"))
            else:
                response = requests.get(RIOT_DDRAGON_CHAMPION_JSON.format(self.lolReleaseVersion, self.ddragonApiLocale))
                self.champion = response.json()
                with codecs.open(championCacheJsonFilePath, "w", "utf-8-sig") as championCacheJsonFile:
                    # championCacheJsonFile.write(u'\ufeff')
                    json.dump(self.champion, championCacheJsonFile)

            self._championKey2LocalName = {}
            self._championKey2OfficialName = {}
            for championName in self.champion["data"]:
                self._championKey2LocalName[int(self.champion["data"][championName]["key"])] = self.champion["data"][championName]["name"]
                self._championKey2OfficialName[int(self.champion["data"][championName]["key"])] = championName

                

        def changeRegion(self, riotApiRegion, ddragonApiLocale):
            #TODO validate regions
            self.riotApiRegion = riotApiRegion
            self.ddragonApiLocale = ddragonApiLocale
            self._loadChampionData()

        def getSummonerDataByName(self, name):
            # print(urllib.request.urlopen(
            #         RIOT_REST_API_FORMAT.format(
            #             self.riotApiRegion
            #             , URL_PATH_SUMMONERS_BY_NAME.format(urllib.parse.quote(name))
            #             , self.riotApiKey
            #         )
            # ).read())
            response = requests.get(
                RIOT_REST_API_FORMAT.format(
                    self.riotApiRegion
                    , URL_PATH_SUMMONERS_BY_NAME.format(name)
                    , self.riotApiKey
                )
            )
            if response.ok:
                return response.json()
            else:
                return None
        
        def getSummonerCurrentSeasonInfoById(self, id):
            response = requests.get(
                RIOT_REST_API_FORMAT.format(
                    self.riotApiRegion
                    , URL_PATH_SUMMONER_CURRENT_SEASON_INFO.format(id)
                    , self.riotApiKey
                )
            )
            if response.ok:
                seasonRecords = response.json()
                if seasonRecords:
                    for record in seasonRecords:
                        #if record["queueType"] == "RANKED_SOLO_5x5":
                        return record
            return None

        def getSummonerCurrentSeasonInfo(self, name):
            summonerData = self.getSummonerDataByName(name)
            if summonerData != None:
                return self.getSummonerCurrentSeasonInfoById(summonerData["id"])
            return None

        def _getChampionMasteries(self, id):
            response = requests.get(
                RIOT_REST_API_FORMAT.format(
                    self.riotApiRegion
                    , URL_PATH_CHAMPION_MASTERIRES.format(id)
                    , self.riotApiKey
                )
            )
            if response.ok:
                return response.json()[0:10]                
            return None

        def _getRecentMostChampion(self, accountId):
            matchData = self._getCurrentMatchList(accountId, 100)
            laneCounter = defaultdict(int)
            championCounter = defaultdict(int)
            for match in matchData:
                championCounter[match["champion"]] += 1

                if match["lane"] != 'NONE':
                    if match["lane"] == 'BOTTOM':
                        laneCounter[match["role"]] += 1
                    else:
                        laneCounter[match["lane"]] += 1
            return sorted(championCounter.items(), key=lambda cc: cc[1], reverse=True)[0:10], sorted(laneCounter.items(), key=lambda lc: lc[1], reverse=True)[0:10]
        '''
        {
            "matches": [{
                "platformId": "KR",
                "gameId": 5002258680,
                "champion": 13,
                "queue": 420,
                "season": 13,
                "timestamp": 1613282526305,
                "role": "SOLO",
                "lane": "MID"
            }]
        }
        '''
        def _getCurrentMatchList(self, accountId, endIndex = 10):
            response = requests.get(
                RIOT_REST_API_FORMAT.format(
                    self.riotApiRegion
                    , URL_PATH_MATCHLISTS.format(accountId)
                    , self.riotApiKey
                )
                + "&beginIndex=0&endIndex={}".format(endIndex)
            )
            if response.ok:
                return response.json()["matches"]
            return []
        def getCurrentMatchList(self, name):
            summonerData = self.getSummonerDataByName(name)
            if summonerData != None:
                return self._getCurrentMatchList(summonerData["accountId"])
            return []
        
        def _getMatchData(self, matchId):
            response = requests.get(
                RIOT_REST_API_FORMAT.format(
                    self.riotApiRegion
                    , URL_PATH_MATCHDATA.format(matchId)
                    , self.riotApiKey
                )
            )
            if response.ok:
                return response.json()
            else:
                return None
        # result : Json text
        # on success payload like this
        # {
        #     "freeChampionIds": [Integers],
        #     "freeChampionIdsForNewPlayers": [Integers],
        #     "maxNewPlayerLevel": Integer
        # }
        def getChampionRotation(self):
            url = RIOT_REST_API_FORMAT.format(self.riotApiRegion, URL_PATH_CHAMPION_ROTATION, self.riotApiKey)
            response = requests.get(url)
            if response.ok:
                result = response.json()
                return [freeChampionId for freeChampionId in result["freeChampionIds"]]
                # return [RIOT_DDRAGON_CHAMPION_SQUARE_ASSETS.format(self.lolReleaseVersion, self._championKey2Name[freeChampionId]) for freeChampionId in result["freeChampionIds"]]
            else:
                print('error')
                #TODO show error
                return []

    return _riotApiManager(riotApiKey)

def createRiotApiManager(riotApiKey):
    return _riotApiManagerGenerator(riotApiKey)