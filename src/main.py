# general
import json

# module
from resource.stringconstant import *
from functional._discord_manager import discordBotRun
from functional._riot_manager import createRiotApiManager

# keyManager = {
#     "discordBotToken": "key value, String",
#     "riotApiKey": "key value, String"
# }
keyManager = json.load(open('./key.json', 'r'))

riotApiManager = createRiotApiManager(keyManager["riotApiKey"])
discordBotRun(riotApiManager, keyManager["discordBotToken"])
#discordBotRun(createRiotApiManager(keyManager["riotApiKey"]), keyManager["discordBotToken"])