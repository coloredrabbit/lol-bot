def _imageManagerGenerator(imageResourcePath, imageResourceVersion):
    # IMAGE_RESOURCE_PATH = './resource/_cache/dragontail'
    # IMAGE_RESOURCE_VERSION = '9.3.1'

    PATH_CHAMPION_IMG_MINI_SIZE_BASE = '{}/{}/img/champion'.format(
                                        imageResourcePath
                                        , imageResourceVersion
                                    )
    PATH_CHAMPION_IMG_MINI_SIZE = PATH_CHAMPION_IMG_MINI_SIZE_BASE + '/{}.png'

    class imageManagerManager:
        def getPathChampionImgMiniSize(championName):
            return PATH_CHAMPION_IMG_MINI_SIZE.format(championName)
    
    return imageManagerManager()

def createImageManager(imageResourcePath, imageResourceVersion):
    return _imageManagerGenerator(imageResourcePath, imageResourceVersion)