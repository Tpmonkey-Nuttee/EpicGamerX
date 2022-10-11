import discord
from discord.ext import commands
from discord.ext import tasks

from bot import Bot
import logging

import datetime
import random

log = logging.getLogger(__name__)

GUILD_ID = 773426467492069386
ANNOUCE_CHANNEL = 973595833968787476

BUFF = {
    "518063131096907813": 5,     # Me
    "401363519523782658": 1,     # Pao
    "881386447532331018": 0,     # Pentor second acc
    "372687500596215808": 1,     # Fluke
    "630963785976250388": 1,     # DoubleQ
    "796676435502694401": 1,     # Thai
    "407378280799404032": 1,     # Pentor    
}

PUNISHMENT = [
    0,
    10,
    60,
    300,
    600,
    1800,
    3600,
]

ROLES = [
    1028840756754006066,  # Red
    1028841106567340102,  # Blue
    1028841349509828689,  # Moon
    1028841449669804166,  # Black
    1028841569656262697,  # White
    0000000000000000000,  # Unknown
]

CHANNELS = [
    1028839187488710698,  # Edge
    1028839243142922241,  # Forest
    1028839291637477427,  # Fault
    1028839408612413531,  # Giant
    1028839444305940551,  # Sea
    1028839533049028718,  # Capital
    1028839565240311828,  # Final
]

HOURS = [
    0,              # Level 0
    10 * 60,        # Level 1
    25 * 60,        # Level 2
    60 * 60,        # Level 3
    150 * 60,       # Level 4
    300 * 60,       # Level 5
    float("inf")    # Level 6
]


class Abyss(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.data = None
        self.guild = None
        self.channel = None

        self.in_vc = []

        self.loop.start()

    def cog_unload(self):
        self.loop.cancel()

    def save(self) -> None:
        self.bot.database.dumps("ABYSS", self.data)

    def get_role(self, id: int) -> None:
        return discord.utils.get(self.guild.roles, id=id)

    def register_in_voice(self, id: int) -> None:
        id = str(id)
        if id not in self.in_vc:
            self.in_vc.append(id)
            print("Registered to vc", id)

    def remove_from_voice(self, id: int) -> None:
        id = str(id)
        if id in self.in_vc:
            self.in_vc.remove(id)
            print("Removed from vc", id)

    def register_profile(self, id: int):
        if id in self.data:
            return

        self.data[id] = {"Level": 1, "Point": 0}

        print("Registered profile", id)

    async def update_role(self, id: int, lv: int) -> None:
        id = int(id)
        member = self.guild.get_member(id)

        before = self.get_role(ROLES[lv - 1])
        after = self.get_role(ROLES[lv])

        if after is not None:
            await member.add_roles(after)
            await member.remove_roles(before)

    async def annouce(self, id: str, lv: int) -> None:
        await self.channel.send(embed=discord.Embed(
            description=
            f"ขอแสดงความยินดีด้วยนักสำรวจ <@{id}> \nคุณได้รับการเลื่อนขั้นเป็น <@&{ROLES[lv]}> แล้ว",
            timestamp=datetime.datetime.utcnow(),
        ))

    async def add_point(self, id: int, amount: int = 1):
        id = str(id)
        self.register_profile(id)

        self.data[id]["Point"] += amount

        lv = self.data[id]["Level"]
        point = self.data[id]["Point"]
        print(f"{id}: {point} +{amount}")

        if point >= HOURS[lv]:
            self.data[id]["Level"] += 1
            self.data[id]["Point"] = 0

            if lv == 5:
                return await self.channel.send(
                    embed = discord.Embed(
                        description = f"ขอแสดงความยินดีด้วยนักสำรวจ <@{id}> \n"
                        "คุณได้มาถึงจุดที่ลึกที่สุดของ The Abyss แล้ว... \n"
                        "ร่างกายของคุณเกิดความเปลี่ยนแปลง... และคุณได้รับพรแห่ง Abyss \n"
                        "คุณสามารถใช้พลัง `!abyssblessing <นักสำรวจ>` เพื่อมอบพลังบางส่วนให้กับนักสำรวจได้",
                        timestamp = datetime.datetime.utcnow()
                    )
                )
            
        
            await self.update_role(id, lv)
            await self.annouce(id, lv)


        self.save()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState) -> None:
        if member.bot:
            return

        if before.channel == after.channel:
            return

        if after.channel is not None:
            if after.channel.id in CHANNELS:
                print("Detected joining")
                # Join, Switch to
                self.register_in_voice(member.id)
            else:
                print("Detecting leaving by switching")
                # Switch to another channel
                self.remove_from_voice(member.id)

        elif after.channel is None:
            # Leave
            print("Detecting leaving")
            self.remove_from_voice(member.id)

    @tasks.loop(minutes=1)
    async def loop(self) -> None:
        for i in self.in_vc:
            if random.randint(1, 666) == 1:
                await self.add_point(i, 60)
            else:
                await self.add_point(i, BUFF.get(i, 1))

    @loop.before_loop
    async def before_invoke(self) -> None:
        await self.bot.wait_until_ready()
        self.guild = self.bot.get_guild(GUILD_ID)
        self.channel = self.bot.get_channel(ANNOUCE_CHANNEL)
        self.data = dict(await self.bot.database.load("ABYSS"))

        for vc in self.guild.voice_channels:
            if vc.id not in CHANNELS:
                continue

            for member in vc.members:
                if not member.bot:
                    self.register_in_voice(member.id)

    @commands.command(name="rank")
    async def rank(self,
                   ctx: commands.Context,
                   target: discord.Member = None) -> None:
        if not target:
            target = ctx.author

        id = str(target.id)

        if id not in self.data:
            return await ctx.send("ไม่พบข้อมูลนักเดินทาง")

        lv = self.data[id]["Level"]
        exp = self.data[id]["Point"]
        max_exp = HOURS[lv]

        per = round(exp / max_exp * 100, 2)
        bar = int(per // 5)
        none = 20 - bar

        if lv < 6:
            name = "Time needed"
            value = f"〚 {'#' * bar}{'-' * none} 〛 «**{per}%**»"
        else:
            name = "พลังสะสม"
            value = f"«**{exp}%**»"

        embed = discord.Embed(
            description= f"<@&{ROLES[min(lv-1, 4)]}>",
            timestamp=ctx.message.created_at
        ).set_author(
            name=target.name, icon_url=target.avatar_url
        ).add_field(
            name=name,
            value=value
        )

        await ctx.send(embed=embed)

    @commands.command(name="abyssblessing")
    async def abblss(self, ctx: commands.Context, target: discord.Member) -> None:
        id = str(ctx.author.id)

        if id not in self.data:
            return

        if self.data[id]["Level"] < 6:
            return

        tid = str(target.id)

        if tid not in self.data:
            return await ctx.send("เขาคนนั้นไม่ใช่นักสำรวจ...")

        amount = self.data[id]["Point"]

        if amount < 60:
            return await ctx.send("คุณยังมีพลังสะสมไม่พอ...")

        self.data[id]["Point"] = 0
        self.data[tid]["Point"] += amount

        maxp = HOURS[self.data[tid]["Level"]]
        per = round(amount / maxp * 100, 2)

        self.save()

        await ctx.send(
            embed = discord.Embed(
                description = f"คุณได้มอบพลังของคุณให้กับ <@{tid}> ซึ่งนับเป็น «**{per}%**» ของเขาสำหรับการเติบโต"
            )
        )
        
    @commands.command(name="aset")
    @commands.is_owner()
    async def aset(self, ctx: commands.Context, target: discord.Member,
                   level: int) -> None:
        self.data[str(target.id)]["Level"] = level
        self.save()

    @commands.command(name="aadd")
    @commands.is_owner()
    async def aadd(self, ctx: commands.Context, target: discord.Member,
                   amount: float) -> None:
        self.data[str(target.id)]["Point"] += amount
        self.save()
    
    @commands.command(name="aanounce")
    @commands.is_owner()
    async def aanounce(self, ctx: commands.Context, target: discord.Member,
                   level: int) -> None:
        await self.annouce(str(target.id), level)
    


def setup(bot: Bot) -> None:
    bot.add_cog(Abyss(bot))
