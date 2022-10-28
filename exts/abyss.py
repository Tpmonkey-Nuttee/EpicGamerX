import discord
from discord.ext import commands
from discord.ext import tasks

from bot import Bot
import logging

import math
import random
import datetime

log = logging.getLogger(__name__)

START = 1665391604

GUILD_ID = 773426467492069386
ANNOUCE_CHANNEL = 1029691542891417610

NO_U = [
    407378280799404032,
    432773406480531467
]

BUFF = {
    "518063131096907813": 5,     # Me
    "401363519523782658": 1,     # Pao
    "881386447532331018": 0,     # Pentor2
    "372687500596215808": 1,     # Fluke
    "630963785976250388": 1,     # DoubleQ
    "796676435502694401": 1,     # Thai
    "407378280799404032": 1,     # Pentor
    "432773406480531467": 1,     # Nig
}

PUNISHMENT = [
    0,     # Edge     -> ?
    10,    # Forest   -> Edge
    20,    # Fault    -> Forest
    30,    # Giant    -> Fault
    60,    # Sea      -> Giant
    120,   # Capital  -> Sea
    300,   # Final    -> Capital
]

ROLES = [
    1028840756754006066,  # Red
    1028841106567340102,  # Blue
    1028841349509828689,  # Moon
    1028841449669804166,  # Black
    1028841569656262697,  # White
    0000000000000000000,  # Place holder
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
    10 * 60,        # Level 1 -  10h -   600s
    25 * 60,        # Level 2 -  25h -  1500s
    60 * 60,        # Level 3 -  60h -  3600s
    150 * 60,       # Level 4 - 150h -  9000s
    300 * 60,       # Level 5 - 300h - 18000s
    float("inf")    # Level 6
]

CURSE_TYPES = [
    "mute", "deaf"
]

class AbyssCurse:
    def __init__(self, bot: Bot, channel: discord.TextChannel):
        self.bot = bot
        self.channel = channel
        self.tasks = {}

    def start(self) -> None:
        if not self.remove_curse.is_running():
            self.remove_curse.start()

    def is_cursed(self, member: discord.Member) -> None:
        return member.id in self.tasks and self.tasks[member.id]['time'] > 3

    async def safe_mute(self, member: discord.Member, mute: bool) -> None:
        typ = self.tasks[member.id]['type'] == "mute"
        
        try:
            if typ:
                await member.edit(mute=mute)
            else:
                await member.edit(deafen=mute)
        except discord.HTTPException:
            pass
    
    async def apply(self, member: discord.Member, level: int, to: int = 0) -> None:
        if member.id in NO_U:
            return
        
        if level < 0:
            return

        level = min(6, level)
        
        if to > level:
            return
    
        mute_time = sum([PUNISHMENT[i] for i in range(level+1) if i > to])
        if mute_time == 0:
            return

        typ = random.choice(CURSE_TYPES)
        if member.id not in self.tasks:
            self.tasks[member.id] = {
                "member": member,
                "time": 0,
                "type": typ
            }
            
            
        await self.safe_mute(member, True)
            
        self.tasks[member.id]["time"] += mute_time
        text = 'ไม่สามารถพูดได้' if typ == 'mute' else 'หูหนวก'
        await self.channel.send(
            embed = discord.Embed(
                description = f"นักเดินทาง {member.mention} ถูกคำสาปแห่ง Abyss!\nเขาจะ{text}เป็นเวลา **{format(self.tasks[member.id]['time'], ',')}** วินาที",
                timestamp = datetime.datetime.utcnow()
            ).set_author(name = "The Curse of the Abyss has been activated!")
        )
        print(f"Applied {typ} to {member.name} for {self.tasks[member.id]['time']}(+{mute_time}) sec")

        self.start()
        
    @tasks.loop(seconds = 1)
    async def remove_curse(self) -> None:
        if len(self.tasks) == 0:
            self.remove_curse.cancel()
        
        for i in self.tasks:
            self.tasks[i]['time'] -= 1
            
            if self.tasks[i]['time'] == 0:
                await self.safe_mute(self.tasks[i]['member'], False)

        for i in self.tasks.copy():
            if not self.tasks[i]['time']:
                del self.tasks[i]
                print("Remove curse for", i)
                


class Abyss(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.data = None
        self.guild = None
        self.channel = None

        self.curse = None

        self.in_vc = []

        self.loop.start()

    def cog_unload(self):
        self.loop.cancel()
        self.curse.remove_curse.cancel()
    
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


    async def add_point(self, id: int, amount: int = 1) -> None:
        id = str(id)
        self.register_profile(id)

        self.data[id]["Point"] += amount

        lv = self.data[id]["Level"]
        point = self.data[id]["Point"]
        print(f"{id}: {point}/{HOURS[lv]} +{amount}")

        if point >= HOURS[lv]:
            print(f"{id}: Leveled up {lv} -> {lv+1}")
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
            if self.curse.is_cursed(member) and member.id not in NO_U and (before.mute or before.deaf):
                await self.curse.safe_mute(member, True)
            return

        if after.channel is not None:
            if after.channel.id in CHANNELS:
                # Join, Switch to
                self.register_in_voice(member.id)
                if before.channel is not None:
                    try:
                        lv = CHANNELS.index(before.channel.id)
                    except ValueError:
                        lv = -1
                    await self.curse.apply(member, lv, CHANNELS.index(after.channel.id))
            else:
                # Switch to another channel
                self.remove_from_voice(member.id)

                if before.channel is not None:
                    await self.curse.apply(member, CHANNELS.index(before.channel.id))

        elif after.channel is None:
            # Leave
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
        self.curse = AbyssCurse(self.bot, self.channel)

        for vc in self.guild.voice_channels:
            if vc.id not in CHANNELS:
                continue

            for member in vc.members:
                if not member.bot:
                    self.register_in_voice(member.id)

    @staticmethod
    def progress_bar_str(progress : float, width : int):
        # 0 <= progress <= 1
        progress = abs(min(1, max(0, progress)) - 1)
        whole_width = math.floor(progress * width)
        remainder_width = (progress * width) % 1
        part_width = math.floor(remainder_width * 5)
        part_char = ["✶", "✷", "✸", "✹", "✺"][part_width]
        if (width - whole_width - 1) < 0:
          part_char = ""
        line = "《 " + "-" * whole_width + part_char + "`" + " " * (width - whole_width - 1) + " ` 》"
        return line

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

        per = exp / max_exp
        perr = round((1 - per) * 100, 2)

        if lv < 6:
            name = "แสงสว่างในจิตใจของคุณ"
            value = f"{self.progress_bar_str(per, 20)} «**{perr}%**»"
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
