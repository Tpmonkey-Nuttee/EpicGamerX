from discord.ext import commands
from discord import Message

from bot import Bot

NAMES_ID = {
    "nig": 432773406480531467,
    "phoori": 331047105571586048,
    "thai": 796676435502694401,
    "pentor": 407378280799404032,
    "pao": 401363519523782658,
    "god": 528800336367058954,
    "no": 518063131096907813,
    "ryu": 584005308037464089,
    "iq": 854587605241036810,
    "name": 702082659173662742,
    "tata": 440148756118241282,
    "monkey": 773468463619375104,
    "pupa": 539447076933730312,
    "bon": 681023373358399508,
    "fluke": 372687500596215808
}

def _(names: list) -> str:
    a = ""
    for n in names:
        id = NAMES_ID.get(n)
        if id is not None:
            a += "<@!{}>".format(id)
    return a

class CustomPing(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    
    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.guild is None: return
        if message.guild.id != 773426467492069386: return
        if message.author.bot: return

        content = message.content.lower()
        if not content.startswith("ping"):
            return
        
        if content == "ping":
            users = [i for i in NAMES_ID]
            return await message.channel.send(f"Pingable Users: {', '.join(users)}")
        
        users = content.split()
        users.pop(0)

        pings = []
        for name in users:
            try:
                pings.append(f"<@!{NAMES_ID[name]}>")
            except KeyError:
                pings.insert(0, f"Unable to find {name}")
        
        await message.channel.send(", ".join(pings))

def setup(bot: Bot) -> None:
    bot.add_cog(CustomPing(bot))