from discord.ext.commands import Cog
from discord import Embed, Colour, Webhook, AsyncWebhookAdapter

from bot import Bot

import datetime
import time

ping = "823178455507927090>"
url = "https://discord.com/api/webhooks/978223454354563092/ewvMea4E9E5Tdr1Jb5a60Hf6_qb8j2EOvd2qVKqmjsUGSr4hTZ8kq9Zszoa4FPftUawm"
avatar = "https://cdn.discordapp.com/avatars/823178455507927090/7a0256f8cd22c127fe5f6c79b77a2f3a.webp"


MESSAGES = (
    "...", "stop", "stop it", "I said... STOP", "???", "https://tenor.com/view/stop-it-get-some-help-gif-7929301",
    "Why are you keep pinging me!!!",
    "What the hell is wrong with you!!!", "I DON'T CARE ABOUT YOU!",
    "...", "You are still going huh?", "Are you that bored?", "I think you're bored.",
    "Go touch some grass?", "No?", "And again?", "...", "I see", "I'm not joking if you still keep doing this I will kick you!", "This is a warning, Stop now", "3", "2...", "1......", "That's it... wait Where is my power?",
    "WHY CAN'T I KICK YOU OUT!?", "...", "Welp, Fuck this", "Adios", "...", "...", "...",
    "...", "...", "...", "...", "...", "...", "...", "...", "...", "Why are you still here?",
    "I can't stay here for much longer, My owner will kill me!", "Go do your work!", "...", "...", "...", "...",
    "I said, GO DO YOUR WORK", "This is just, Nuttee's Insanity! so STOP IT!", "...", "...", "...", "...", "...", "...",
    "You are... still doing it?", "...", "...", "...", "You know how much time did you spend pinging me?",
    "...", "...", "...", "I have nothing left for you. Good bye", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "wow Im actually impressed that you still keep doing it.", "so uh, when will you stop?", "I actually ran out of words here so um...", "... I don't want to say this but", "I believe in you", "If you can be this dedicated on pinging me like this, I believe in you.", "You are good", "You can be happy", "You will have a brighe future", "Keep your head up", "I believe that you can do it", "You can pass on whatever you wanted!", "Thank you for your hard works", "I hope that we can actually meet in person but... I'm just a bot",
    "so all I can say is 'Have a nice day!'", "That's it for me", "Good bye"
)

class PaoNoName(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.counters = 0
        self.time = time.time()
        self.webhook = None
    
    @Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild.id != 773426467492069386:
            return

        if self.webhook is None:
            self.webhook = Webhook.from_url(url, adapter = AsyncWebhookAdapter(self.bot.trust_session))

        if before.nick != after.nick:
            embed = Embed(
                colour = Colour.random(),
                timestamp = datetime.datetime.utcnow()
            )
            embed.set_author(name=after, icon_url=after.avatar_url)
            embed.add_field(name="From:", value = before.nick if before.nick is not None else before.name)
            embed.add_field(name="To:", value = after.nick if after.nick is not None else after.name)

            await self.webhook.send(
                embed = embed,
                username = "NickName Log",
                avatar_url = avatar,
            )
    
    @Cog.listener()
    async def on_message(self, message):
        #if message.guild is None or message.guild.id != 773426467492069386:
        #    return
        
        if ping in message.content:
            await self.stop(message)
    
    async def stop(self, message):
       
        self.counters += 1
        n = self.counters

        if time.time() - self.time >= 1800:
            self.time = time.time()
            self.counters = 0

        if n - 2 >= len(MESSAGES):
            return await message.channel.send("...")
        if n >= 2:
            return await message.channel.send(MESSAGES[n-2])       

def setup(bot: Bot) -> None:
    bot.add_cog(PaoNoName(bot))