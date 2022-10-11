from discord.ext import commands
from discord.ext import tasks
import discord

from bs4 import BeautifulSoup
import datetime
import asyncio

import logging

log = logging.getLogger(__name__)

URL = "https://www.vlr.gg/"
CHANNEL_ID = 962693537458188308

class VCT(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.data = []
        
        self.messages = []
        self.channel = None
        
        self.loop.start()

    def cog_unload(self) -> None:
        self.loop.cancel()

    @tasks.loop(minutes = 3)
    async def loop(self) -> None:
        await self.fetch()
        await self.update()

    @loop.before_loop
    async def get(self) -> None:
        await self.bot.wait_until_ready()

        self.channel = self.bot.get_channel(CHANNEL_ID)

        async for mess in self.channel.history(limit=30):
            if mess.author.id == self.bot.user.id:
                self.messages.append(mess)

                if len(self.messages) >= 8:
                    return
                
        

    async def fetch(self) -> None:
        r = await self.bot.trust_session.get(URL)
        r = await r.text()
        await self.format(r)

    async def format(self, txt: str) -> None:
        soup = BeautifulSoup(txt, "html.parser")
        panel = soup.find(attrs={"class":"wf-module wf-card mod-home-matches"})

        if panel is None:
            log.warning("cannot get panel")

        # Links
        links = [f'{URL}{a.get("href")}' for a in panel.find_all("a")]
        
        # Series & Events
        times = panel.find_all("div", attrs={"class":"h-match-preview"})
        series = []
        events = []
        
        for _ in times:
            a = _.find("div", attrs={"class":"h-match-preview-series"}).get_text().strip()
            b = _.find("div", attrs={"class":"h-match-preview-event"}).get_text().strip()
        
            series.append(a)
            events.append(b)
            
        
        # Teams names, Time
        teams = panel.find_all("div", attrs={"class":"h-match-team"})
        # "h-match-eta mod-final"
        # "h-match-eta mod-live"
        # "h-match-eta mod-upcoming"
        
        data = []
        
        
        i = 1
        for team in teams:
            
            name = team.find("div", attrs={"class":"h-match-team-name"}).get_text().strip()    
            score = team.find("div", attrs={"class":"h-match-team-score mod-count js-spoiler"})
            if score is None:
                score = "-"
            else:
                score = score.get_text().strip()
        
        
            if i % 2 != 0:
                # reset        
                payload = {}
                
                # first team
                current = team.find("div", attrs={"class":"h-match-eta mod-final"})
                if current is None:
                    current = team.find("div", attrs={"class":"h-match-eta mod-live"})
                    if current is None:
                        current = team.find("div", attrs={"class":"h-match-eta mod-upcoming"})
                        if current is None:
                            current = team.find("div", attrs={"class":"h-match-eta mod-live mod-nostream"})
                            if current is None:
                                current = team.find("div", attrs={"class":"h-match-eta"})

                if current is not None:
                    current = current.get_text().strip()
                else:
                    await self.bot.get_user(518063131096907813).send(
                        str(team.find_all("div"))
                    )
                    current = "Unnown div class"
        
                payload["team1"] = name
                payload["team1_score"] = score
                payload["current"] = current
            else:
                payload["team2"] = name
                payload["team2_score"] = score
        
                data.append(payload)
            
            i += 1
        
        for i, item in enumerate(data):
            item["link"] = links[i]
            item["serie"] = series[i]
            item["event"] = events[i]
            data[i] = item

        self.data = data[:8]

    async def get_embeds(self) -> discord.Embed:
        embeds = []
        
        for data in self.data:
            embed = discord.Embed(
                description = f"[**{data['current']}**]({data['link']})",
                timestamp = datetime.datetime.utcnow()
            ).set_footer(text = "Last Update")

            name = f"{data['team1']} {data['team1_score']} vs {data['team2_score']} {data['team2']}"
            embed.set_author(name = name, url = data['link'])

            embed.add_field(name = "Event", value = f'{data["event"]}\n*{data["serie"]}*')

            embeds.append(embed)

        return embeds
    
    async def update(self) -> None:
        embeds = await self.get_embeds()

        for i in range(8):
            try:
                message = self.messages[i]
            except IndexError:
                m = await self.channel.send(embed = embeds[i])
                self.messages.append(m)

                await asyncio.sleep(20)
                continue

            if message.embeds[0] == embeds[i]:
                continue
            
            await message.edit(embed=embeds[i])
            await asyncio.sleep(20)
            
        # if self.message is None:
        #     self.message = await self.channel.send(embed=embed)            
        # else:
        #     if self.message.embeds[0] != embed:
        #         await self.message.edit(content = "", embed=embed)

def setup(bot: commands.Bot) -> None:
    return
    bot.add_cog(VCT(bot))