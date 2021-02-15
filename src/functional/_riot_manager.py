# riot api imports
from riotwatcher import LolWatcher, ApiError
import pandas as pd

# lolWatcher = LolWatcher(keyManager.riotApiKey)

#TODO
def _riotApiManagerGenerator():
    class _riotApiManager:
        validRegions = ['BR1', 'EUN1', 'EUW1', 'JP1', 'KR', 'LA1', 'LA2', 'NA1', 'OC1', 'TR1', 'RU']
        lolWatcherRegion = 'kr' #default value: kr
        key = ''

        def setKey(key):
            self.key = key

    return _riotApiManager

def createDiscordManager():
    return _discrodManagerGenerator()