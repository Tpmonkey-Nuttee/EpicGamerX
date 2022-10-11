from discord.ext.commands import command, Cog, Context

from bot import Bot

import datetime

class RiseofKingdoms(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    
    @command()
    async def speedups(
        self, ctx: Context,
        min1: int, min5: int = 0, min10: int = 0, min15: int = 0, min30: int = 0,
        min60: int = 0, hour3: int = 0, hour8: int = 0, hour15: int = 0, hour24: int = 0,
        day3: int = 0, day7: int = 0, day15: int = 0, day30: int = 0
    ):
        await ctx.send(
            datetime.timedelta(
                minutes = min1 + min5 * 5 + min10 * 10 + min15 * 15 + min30 * 30 + min60 * 60 \
                + hour3 * 60 * 3 + hour8 * 60 * 8 + hour15 * 60 * 15 + hour24 * 60 * 24 \
                + day3 * 24 * 3 + day7 * 24 * 7 + day15 * 24 * 15 + day30 * 24 * 30
            )   
        )

def setup(bot: Bot) -> None:
    bot.add_cog(RiseofKingdoms(bot))