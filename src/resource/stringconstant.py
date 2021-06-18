# paths
PATH_KEY_JSON_FILE='./key.json'

# global
URL_PATH_CHAMPION_ROTATION='/lol/platform/v3/champion-rotations'
URL_PATH_SUMMONERS_BY_NAME='/lol/summoner/v4/summoners/by-name/{}' # param: summonerName
URL_PATH_SUMMONER_CURRENT_SEASON_INFO = '/lol/league/v4/entries/by-summoner/{}' # param: encryptedSummonerId

URL_PATH_MATCHLISTS = '/lol/match/v4/matchlists/by-account/{}' # param: encryptedAccountId
URL_PATH_MATCHDATA = '/lol/match/v4/matches/{}' #param: matchId(gameId)

URL_PATH_CHAMPION_MASTERIRES = '/lol/champion-mastery/v4/champion-masteries/by-summoner/{}' # param: encryptedSummonerId

'''
/riot/account/v1/accounts/by-puuid/{puuid}
/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}
/riot/account/v1/active-shards/by-game/{game}/by-puuid/{puuid}

[DONE] /lol/champion-mastery/v4/champion-masteries/by-summoner/{encryptedSummonerId}
/lol/champion-mastery/v4/champion-masteries/by-summoner/{encryptedSummonerId}/by-champion/{championId}
/lol/champion-mastery/v4/scores/by-summoner/{encryptedSummonerId}

[DONE] /lol/platform/v3/champion-rotations

/lol/clash/v1/players/by-summoner/{summonerId}
/lol/clash/v1/teams/{teamId}
/lol/clash/v1/tournaments
/lol/clash/v1/tournaments/by-team/{teamId}
/lol/clash/v1/tournaments/{tournamentId}

/lol/league-exp/v4/entries/{queue}/{tier}/{division}

/lol/league/v4/challengerleagues/by-queue/{queue}
/lol/league/v4/entries/by-summoner/{encryptedSummonerId}
/lol/league/v4/entries/{queue}/{tier}/{division}
/lol/league/v4/grandmasterleagues/by-queue/{queue}
/lol/league/v4/leagues/{leagueId}
/lol/league/v4/masterleagues/by-queue/{queue}

/lol/status/v3/shard-data

/lol/status/v4/platform-data

/lor/match/v1/matches/by-puuid/{puuid}/ids
/lor/match/v1/matches/{matchId}

/lor/ranked/v1/leaderboards

/lor/status/v1/platform-data

[DONE] /lol/match/v4/matches/{matchId}
[DONE] /lol/match/v4/matchlists/by-account/{encryptedAccountId}
/lol/match/v4/timelines/by-match/{matchId}
/lol/match/v4/matches/by-tournament-code/{tournamentCode}/ids
/lol/match/v4/matches/{matchId}/by-tournament-code/{tournamentCode}

/lol/spectator/v4/active-games/by-summoner/{encryptedSummonerId}
/lol/spectator/v4/featured-games

/lol/summoner/v4/summoners/by-account/{encryptedAccountId}
[DONE] /lol/summoner/v4/summoners/by-name/{summonerName}
/lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}
/lol/summoner/v4/summoners/{encryptedSummonerId}

/tft/league/v1/challenger
/tft/league/v1/entries/by-summoner/{encryptedSummonerId}
/tft/league/v1/entries/{tier}/{division}
/tft/league/v1/grandmaster
/tft/league/v1/leagues/{leagueId}
/tft/league/v1/master

/tft/match/v1/matches/by-puuid/{puuid}/ids
/tft/match/v1/matches/{matchId}

/tft/summoner/v1/summoners/by-account/{encryptedAccountId}
/tft/summoner/v1/summoners/by-name/{summonerName}
/tft/summoner/v1/summoners/by-puuid/{encryptedPUUID}
/tft/summoner/v1/summoners/{encryptedSummonerId}

/lol/platform/v4/third-party-code/by-summoner/{encryptedSummonerId}

/lol/tournament-stub/v4/codes
/lol/tournament-stub/v4/lobby-events/by-code/{tournamentCode}
/lol/tournament-stub/v4/providers
/lol/tournament-stub/v4/tournaments

/lol/tournament/v4/codes
GET /lol/tournament/v4/codes/{tournamentCode}
PUT /lol/tournament/v4/codes/{tournamentCode}
/lol/tournament/v4/lobby-events/by-code/{tournamentCode}
/lol/tournament/v4/providers
/lol/tournament/v4/tournaments

/val/content/v1/contents

/val/match/v1/matches/{matchId}
/val/match/v1/matchlists/by-puuid/{puuid}
/val/match/v1/recent-matches/by-queue/{queue}

/val/ranked/v1/leaderboards/by-act/{actId}

/val/status/v1/platform-data
'''

# message
MSG_WELCOME_TO_DC_GG='welcome to dc.gg'
MSG_CURRENT_PARTICIPANTS='Current participants'
MSG_SHOW_ROTATION='Rotation'
MSG_FREE_CHAMPION='Free champions'

MSG_PARTICIPANTS_ADDED_SUCCESSFULLY='participants added successfully.'
MSG_PARTICIPANTS_REMOVED_SUCCESSFULLY='participants removed successfully.'

MSG_TERMINATE_SERVER='Terminate server...'

TIER_NOT_FOUND='No tier exist'

# error message
MSG_ERR_TITLE='Error'
MSG_ERR_ADDING_PARTICIPANTS='Cannot add the participants cause by {}'
MSG_ERR_REMOVING_PARTICIPANTS='Cannot remove the participants cause by {}'
MSG_ERR_SUMMONER_NOT_FOUND='No summoner exists'

# plain string resource
TIER_UNRANK='[Unrank]'