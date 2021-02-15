# general
import json

# module
from functional._discord_manager import *
from resource.stringconstant import *
# from functional._riot_manager import *


# keyManager = {
#     "discordBotToken": "key value, String",
#     "riotApiKey": "key value, String"
# }
keyManager = json.load(open('./key.json', 'r'))

# riotApiManager = createRiotApiManager()
# riotApiManager.setKey(keyManager.riotApiKey)

# discordManager = createDiscordManager(, None)
discordBotRun(keyManager["discordBotToken"])
