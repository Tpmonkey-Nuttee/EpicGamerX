from discord.ext import commands
import discord

from bot import Bot

from typing import Union, Tuple, List
from contextlib import suppress
from random import choice as c
import asyncio

REQUEST_COOLDOWN = 20 # seconds

THUMB_UP = "👍"

ENSURE_VC_TEXTS = [
    "You gotta join vc first!", "You are not in vc. \:(", "Join vc first!",
    "You are not in vc!"
]

NOBODY_IN_VOICE_TEXTS = [
    "Nobody in that vc...", "No-one in that vc!"
]


class VoiceChatRequest(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        self.asks = {}    
        """
        {
            user_id: {
                req_id1: msg or None,
                req_id2: msg or None,
                req_id3: msg or None
            }
        }
        """

        self.info = {}
    
    async def wait_for_cancel(self, user_id: int, timeout: int = 600) -> None:
        await asyncio.sleep(timeout)

        await self.cancel(user_id, "Timeout: Nobody accepted him.")
    
    async def cancel(self, user_id: int, reason: str) -> None:
        ctx = self.info[user_id]['ctx']

        embed = discord.Embed(
            description = reason,
            colour = discord.Colour.dark_red(),
            timestamp = ctx.message.created_at
        ).set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

        for member in self.asks[user_id]:
            msg = self.asks[user_id][member]
            _embed = msg.embeds[0]
            
            with suppress(Exception):
                if embed.colour != _embed.colour:
                    await msg.edit(embed=embed)
        
        with suppress(Exception):
            del self.info[user_id]
        
        with suppress(Exception):
            del self.asks[user_id]
    
    async def send_to_vc(self, user_id: int) -> None:
        ctx = self.info[user_id]['ctx']

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(f"{ctx.author.mention}, Agreed to join but you're not in vc... canceled!")
            return await self.cancel(user_id, "User is not in voice channel, Canceled!")
        
        vc = self.info[user_id]['target_vc']
        try:
            await ctx.author.move_to(vc)
        except Exception as e:
            return await ctx.send(f"Cannot move {ctx.author.mention} to {vc.mention}; Reason: {e}")
        await ctx.send(f"Moved {ctx.author.mention} to {vc.mention}")
        await self.cancel(user_id, "Already accepted & Moved.")
    
    async def confirm(self, user_id: int, accept_id: int) -> None:
        self.info[user_id]['current'] += 1

        ctx = self.info[user_id]['ctx']

        embed = discord.Embed(
            description = "You have accepted the request!",
            colour = discord.Colour.teal(),
            timestamp = ctx.message.created_at
        ).set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

        with suppress(discord.HTTPException, KeyError):
            await self.asks[user_id][accept_id].edit(embed=embed)

        if self.info[user_id]['current'] >= self.info[user_id]['amount_needed']:
            return await self.send_to_vc(user_id) 
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: Union[discord.User, discord.Member]) -> None:
        if len(self.asks) == 0: 
            return

        if reaction.emoji != THUMB_UP:
            return

        target = None
        
        for user_id in self.info:
            if reaction.message.id in self.info[user_id]["msg_ids"]:
                target = user_id
                break
            
        if target is None:
            return
        
        await self.confirm(target, user.id)        


    @commands.command(name="req")
    @commands.cooldown(3, REQUEST_COOLDOWN, commands.BucketType.member)
    async def _req(self, ctx: commands.Context, voice_channel: discord.VoiceChannel) -> None:
        """Request to join locked vc."""

        if len(voice_channel.members) == 0:
            return await ctx.send( c(NOBODY_IN_VOICE_TEXTS) )
        
        if ctx.author.id in self.asks:
            return await ctx.send("Already asked for it!")
        
        if ctx.author.voice.channel == voice_channel:
            return await ctx.send("You're already in it! bruh!!!")

        embed = discord.Embed(
            description = f"Want to join your voice channel! ({voice_channel.mention})\n"
                "React :thumbsup: to confirm!",
            colour = discord.Colour.blue(),
            timestamp = ctx.message.created_at
        ).set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

        self.info[ctx.author.id] = {
            "msg_ids": [], "ctx": ctx, "target_vc": voice_channel,
            "users": [], "user_ids": [],
            "amount": 0, "amount_needed": 0, "current": 0
        }
        
        # Sending msg.
        self.asks[ctx.author.id] = {}
        amount = 0
        for member in voice_channel.members:
            try:
                msg = await member.send(embed=embed)
                await msg.add_reaction(THUMB_UP)
            except discord.HTTPException:
                await ctx.send(f"{member}: Cannot send dm/add reaction! passing...")
                continue
            except discord.Forbidden:
                await ctx.send(f"{member}: Dm is not open!")
                continue
            
            self.asks[ctx.author.id][member.id] = msg

            self.info[ctx.author.id]['msg_ids'].append(msg.id)
            self.info[ctx.author.id]['user_ids'].append(member.id)
            self.info[ctx.author.id]['users'].append(member)

            amount += 1
        
        # tracking
        self.info[ctx.author.id]['amount'] = amount

        # Reply
        amount_needed = self.info[ctx.author.id]['amount_needed'] = min(2, amount)
        await ctx.send(
            f"Request sent to {amount} members! \n"
            f"You will need **{amount_needed}** people in order to join! (timeout in 10 minutes)"
        )
    
    @_req.before_invoke
    async def ensure_in_vc(self, ctx: commands.Context) -> None:
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError( c(ENSURE_VC_TEXTS) )
        

def setup(bot: Bot) -> None:
    bot.add_cog(VoiceChatRequest(bot))