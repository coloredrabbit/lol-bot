import discord

def getDiscordMessageDeveloperInfo():
    # TODO: 이런 정보들은 JSON으로 관리될 수 있음.
    # URLs
    DC_GG_TITLE_URL  = "https://github.com/coloredrabbit/lol-bot"
    AUTHOR_URL       = "https://github.com/coloredrabbit"
    AUTHOR_ICON_URL  = "https://raw.githubusercontent.com/coloredrabbit/lol-bot/main/src/resource/icons/64x64.png"
    THUMBNAIL_URL    = "https://raw.githubusercontent.com/coloredrabbit/lol-bot/main/src/resource/icons/64x64.png"

    GIT_REPOSITORY_URL = "https://github.com/coloredrabbit/lol-bot"
    TRELLO_URL         = "https://trello.com/b/Soq6pOOZ/dcgg"
    NOTION_URL         = "https://www.notion.so/invite/221ec282274b15de66e4e608d2a409debb137085?channel=email"
    CONTACT_US_URL     = ""
    BUG_REPORT_URL     = "https://github.com/coloredrabbit/lol-bot/blob/main/README.md"

    embed=discord.Embed(title="Dc.gg information", url=AUTHOR_LINK, description="Discord @안병현 @김당당", color=0x00b3ff)
    embed.set_author(name="Byung Hyun An", url=AUTHOR_LINK, icon_url=AUTHOR_ICON_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    
    # infoTableContent = """

    # """
    # embed.add_field(name="Links", value=infoTableContent, inline=False)

    embed.add_field(name="Developers", value="안병현, 김다인", inline=False)
    embed.add_field(name="Help", value="https://github.com/coloredrabbit/lol-bot/blob/main/README.md", inline=True)
    embed.add_field(name="Contact", value="https://github.com/coloredrabbit/lol-bot/blob/main/README.md", inline=True)
    embed.add_field(name="Issues", value="https://trello.com/b/Soq6pOOZ/dcgg", inline=True)

    embed.set_footer(text="Copyright (C) 2021 coloredrabbit - The Python Open Source Project")
    return embed
