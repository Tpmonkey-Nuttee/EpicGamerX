from discord.ext import commands
import discord

from bot import Bot


# Main ID: Second ID
MAP = {
    407378280799404032: 881386447532331018,
    # 539447076933730312: 
}

class Pentor(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        if member.id not in MAP:
            return

        if before.channel is None:
            return

        mic = None
        for i in before.channel.members:
            if i.id == MAP[member.id]:
                mic = i
                break

        if mic is None:
            return

        return await mic.move_to(after.channel)

            


def setup(bot: Bot) -> None:
    bot.add_cog(Pentor(bot))