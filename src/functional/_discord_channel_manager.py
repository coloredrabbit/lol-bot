import discord
import os
import ast
import threading
import time

from resource.stringconstant import *

def getDiscordChannelManager():
    FILE_PATH_CHANNEL_DATA = './src/resource/_channel_data.dcgg'

    '''
    connectedChannels {
        {channelId}: {
            "participants" = {
                "id": "",
                "accountId": "",
                "puuid": "",
                "name": "{summonerName}",
                "profileIconId": Integer,
                "revisionDate": Integer,
                "summonerLevel": Integer
            "options": {
                
            }
        }
    }
    '''
    _connectedChannels = {}

    _discordDefaultOption = {
        # light mode - 모든 추가적인 옵션 False
        '_light_mode': False,

        # balance
        '_balace_use_': False,

        # recommanded ban pick
        '_ban_list_size': 12,
        '_ban_enable_mastery': True,
        '_ban_enable_recent_most_champion': True,
        
        # match record 전적
        '_record_list_size': 20,
        '_record_enable_base': True, # champion name, level, kills, deaths, assists, kda
        '_record_enable_lane': True, # lane
    }

    def _save_channel_data():
        global _connectedChannels
        _connectedChannels = (open(FILE_PATH_CHANNEL_DATA, 'w').write(str(_connectedChannels)))
        time.sleep(10)

    def _load_channel_data():
        global _connectedChannels
        if os.path.exists(FILE_PATH_CHANNEL_DATA):
            _connectedChannels = ast.literal_eval(open(FILE_PATH_CHANNEL_DATA, 'r').read())
        else:
            _connectedChannels = {}


    class DiscordChannelManager:
        def __init__(self):
            _load_channel_data()
            
            serverDataSaveTimer = threading.Thread(target=_save_channel_data)
            serverDataSaveTimer.start()

        def _processingChannelExists(self, channelId):
            nonlocal _connectedChannels

            if not channelId in _connectedChannels:
                _connectedChannels[channelId] = {
                    'participants': {},
                    'options': _discordDefaultOption.copy() # or dict(_discordDefaultOption)
                }

        def getParticipants(self, channelId):
            nonlocal _connectedChannels

            self._processingChannelExists(channelId)

            return _connectedChannels[channelId]['participants']

        def getOptions(self, channelId):
            nonlocal _connectedChannels

            self._processingChannelExists(channelId)

            return _connectedChannels[channelId]['options']

        def setParticipants(self, channelId, participants):
            nonlocal _connectedChannels
            _connectedChannels[channelId]['participants'] = participants

        def setOptions(self, channelId, options):
            nonlocal _connectedChannels
            _connectedChannels[channelId]['options'] = participants

    return DiscordChannelManager()