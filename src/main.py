# general
import json

# module
from resource.stringconstant import *
from functional._discord_manager import discordBotRun
from functional._riot_manager import createRiotApiManager
from functional._image_manager import createImageManager

IMAGE_RESOURCE_PATH = './resource/_cache/dragontail'
IMAGE_RESOURCE_VERSION = '9.3.1'

# keyManager = {
#     "discordBotToken": "key value, String",
#     "riotApiKey": "key value, String"
# }
keyManager = json.load(open('./key.json', 'r'))

riotApiManager = createRiotApiManager(keyManager["riotApiKey"])
imageManager = createImageManager(IMAGE_RESOURCE_PATH, IMAGE_RESOURCE_VERSION)

discordBotRun(riotApiManager, imageManager, keyManager["discordBotToken"])
#discordBotRun(createRiotApiManager(keyManager["riotApiKey"]), keyManager["discordBotToken"])
