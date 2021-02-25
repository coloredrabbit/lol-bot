import discord
import os
import ast
import threading
import time
import atexit
import codecs

from resource.stringconstant import *

def getDiscordChannelManager():
    FILE_PATH_CHANNEL_DATA = './src/resource/_channel_data.dcgg'

    '''
    connectedChannels {
        {channelId}: {
            "participants" = {
                "participantsName1": {
                    "id": "",
                    "accountId": "",
                    "puuid": "",
                    "name": "{summonerName}",
                    "profileIconId": Integer,
                    "revisionDate": Integer,
                    "summonerLevel": Integer
                }
                , ...
            },
            "recommandedTeam": [
                "team_hash": {
                    red: ["participantName1", ..., "participantName5"],
                    blue: ["participantName6", ..., "participantName10"]
                }
                , ...
            ],
            "options": {
                
            }
        }
    }
    '''
    _connectedChannels = {}

    _discordDefaultOption = {
        # light mode - 모든 추가적인 옵션 False
        '_light_mode': False,

        '_bring_match_size': 50,

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

        '_recommanded_team_maximum_size': True
    }

    def _save_channel_data():
        nonlocal _connectedChannels
        print('save channel data...')
        with codecs.open(FILE_PATH_CHANNEL_DATA, 'w', 'utf-8-sig') as f:
            f.write(str(_connectedChannels))
    atexit.register(_save_channel_data) # do save before exit

    def _load_channel_data():
        nonlocal _connectedChannels
        if os.path.exists(FILE_PATH_CHANNEL_DATA):
            _connectedChannels = ast.literal_eval(codecs.open(FILE_PATH_CHANNEL_DATA, 'r', 'utf-8-sig').read())
        else:
            _connectedChannels = {}
        for optionKey in _discordDefaultOption:
            for channelId in _connectedChannels:
                if not optionKey in _connectedChannels[channelId]:
                    # !warn: shallow copy
                    _connectedChannels[channelId][optionKey] = _discordDefaultOption[optionKey]


    class DiscordChannelManager:
        def __init__(self):
            _load_channel_data()

        def _processingChannelExists(self, channelId):
            nonlocal _connectedChannels
            if not channelId in _connectedChannels:
                _connectedChannels[channelId] = {
                    'participants': {},
                    'recommandedTeam': [],
                    'options': _discordDefaultOption.copy() # or dict(_discordDefaultOption)
                }

        def getParticipants(self, channelId):
            self._processingChannelExists(channelId)

            return _connectedChannels[channelId]['participants']

        def getRecommandedTeam(self, channelId, hash):
            self._processingChannelExists(channelId)
            
            if not hash in _connectedChannels[channelId]['recommandedTeam']:
                return [], []
            recommandedTeam = _connectedChannels[channelId]['recommandedTeam'][hash]
            return recommandedTeam.red, recommandedTeam.blue

        def getOptions(self, channelId):
            self._processingChannelExists(channelId)

            return _connectedChannels[channelId]['options']

        def setParticipants(self, channelId, participants):
            nonlocal _connectedChannels
            _connectedChannels[channelId]['participants'] = participants

        def setRecommandedTeam(self, channelId, recommandedTeam):
            nonlocal _connectedChannels
            _connectedChannels[channelId]['recommandedTeam'] = recommandedTeam

        def setOptions(self, channelId, options):
            nonlocal _connectedChannels
            _connectedChannels[channelId]['options'] = participants

        def clearChannelData(self, channelId):
            nonlocal _connectedChannels
            _connectedChannels[channelId]['participants'] = []
            _connectedChannels[channelId]['recommandedTeam'] = []

    return DiscordChannelManager()