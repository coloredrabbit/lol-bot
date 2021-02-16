import requests
import json
import os
import codecs

from resource.stringconstant import *

# 1. Region
# 2. Riot API version
# 3. Rest API path
# 4. Riot API key
RIOT_REST_API_FORMAT = "https://{}.api.riotgames.com/lol/platform/{}/{}?api_key={}"


# 1. Riot LOL release version
# 2. region
RIOT_DDRAGON_CHAMPION_JSON = 'http://ddragon.leagueoflegends.com/cdn/{}/data/{}/champion.json'
RIOT_DDRAGON_CHAMPION_JSON_FILE_CACHE_PATH = './src/resource/_cache/{}_{}.json'

RIOT_DDRAGON_CHAMPION_SQUARE_ASSETS = 'http://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}.png'

#TODO
def _riotApiManagerGenerator(riotApiKey):
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
            if(os.path.exists(championCacheJsonFilePath)):
                print('already exist riot champion data')
                self.champion = json.load(codecs.open(championCacheJsonFilePath, 'r', "utf-8-sig"))
            else:
                response = requests.get(RIOT_DDRAGON_CHAMPION_JSON.format(self.lolReleaseVersion, self.ddragonApiLocale))
                self.champion = response.json()
                with codecs.open(championCacheJsonFilePath, "w", "utf-8-sig") as championCacheJsonFile:
                    # championCacheJsonFile.write(u'\ufeff')
                    json.dump(self.champion, championCacheJsonFile)

            # print(self.champion) # !debug

            #TODO convert to dict comprehensive
            # self._championKey2Name = {k: name, for championName in self.champion["data"] }
            self._championKey2Name = {}
            for championName in self.champion["data"]:
                self._championKey2Name[int(self.champion["data"][championName]["key"])] = self.champion["data"][championName]["name"]
                # self._championKey2Name[int(self.champion["data"][championName]["key"])] = championName
            
            # print(self._championKey2Name) # !debug

        def changeRegion(self, riotApiRegion, ddragonApiLocale):
            #TODO validate regions
            self.riotApiRegion = riotApiRegion
            self.ddragonApiLocale = ddragonApiLocale
            self._loadChampionData()


        # result : Json text
        # on success payload like this
        # {
        #     "freeChampionIds": [Integers],
        #     "freeChampionIdsForNewPlayers": [Integers],
        #     "maxNewPlayerLevel": Integer
        # }
        def getChampionRotation(self):
            url = RIOT_REST_API_FORMAT.format(self.riotApiRegion, 'v3', URL_PATH_CHAMPION_ROTATION, self.riotApiKey)
            response = requests.get(url)
            if(response.ok):
                result = response.json()
                return [self._championKey2Name[freeChampionId] for freeChampionId in result["freeChampionIds"]]
                # return [RIOT_DDRAGON_CHAMPION_SQUARE_ASSETS.format(self.lolReleaseVersion, self._championKey2Name[freeChampionId]) for freeChampionId in result["freeChampionIds"]]
            else:
                print('error')
                #TODO show error
                return []

    return _riotApiManager(riotApiKey)

def createRiotApiManager(riotApiKey):
    return _riotApiManagerGenerator(riotApiKey)