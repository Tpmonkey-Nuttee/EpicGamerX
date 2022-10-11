# Admin stuff for the bot
# Made by Tpmonkey

from discord.ext.commands import is_owner, command, Cog, Context
from discord import Embed, Color, TextChannel

from utils.extensions import EXTENSIONS
from bot import Bot

import logging
from typing import Optional

# These library is for admin eval command
import traceback
import datetime
import inspect
import importlib
import discord
import os
import math
import time

log = logging.getLogger(__name__)

class AdminCommands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.eval_jobs = {}
        self.clear = False
    
    
    def delete_eval_job(self, id: int) -> None:
        # Delete existing eval job.
        # Need except if the command has been run twice at the same time
        try:
            del self.eval_jobs[id]
        except Exception as e:
            log.trace(f"Couldn't delete eval job; {e}")
            pass
    
    @command()
    @is_owner()
    async def stoprn(self, ctx: Context) -> None:
        self.clear = False
 
        await ctx.send("It should stop, I hope.")
    
    @command()
    @is_owner()
    async def clearm(self, ctx: Context, amount: int = 99999) -> None:
        self.clear = True
        i = 0

        async for mess in ctx.channel.history(limit=amount):
            try:
                await mess.delete()
            except:
                pass
            else:
                i+=1
                
            if not self.clear:
                break

        self.clear = False

        await ctx.send(f"Deleted **{i}** messages.")

    @command(name="say")
    @is_owner()
    async def say(self, ctx: Context, channel: Optional[TextChannel], *, text: str) -> None:
        # Make the bot say something, FOR FUN (Admn only :P)
        delete = True
        text = "".join(text)

        if "--nodelete" in text or "--nod" in text:
            text = text.replace("--nodelete", "")  
            text = text.replace("--nod", "")
            delete = False        
        
        if delete:
            await ctx.message.delete()
        log.debug(f"Say: {text},  Delete: {delete}")

        try:
            await channel.send(text)
        except:
            await ctx.send(text)

    @command(name='admineval', aliases = ("ae", ), help = 'Admin command for testing!')
    @is_owner()
    async def _eval(self, ctx: Context, *,  code: str) -> None:
        # Admin eval command
        code = code.strip("```")
        send = True
        
        log.debug(f"Admin Eval from {ctx.author}; code: {code}")

        # Custom options
        if "--nooutput" in code:
            code = code.replace("--nooutput", "")
            send = False
        if "--delete" in code:
            code = code.replace("--delete", "")
            await ctx.message.delete()
        
        # Run the code
        if "import" in code and "exec" not in code:
            code_ = code.replace("import ", "")
            try:
                self.mod = importlib.import_module(code_)
            except:
                result = traceback.format_exc()
            else:
                result = self.mod

        else:            
            try:
                result = await eval( str(code).replace("await ", "") ) if "await" in code else eval(code)
            except:
                result = traceback.format_exc()

        # In case of output is longer than Discord allowed, I use list of embed and send it one by one
        embeds = await self._format(ctx, code, result)
        if not send:
            return
        
        self.eval_jobs[ctx.author.id] = embeds      

        for embed in self.eval_jobs[ctx.author.id]:
            if ctx.author.id not in self.eval_jobs:
                break
            
            await ctx.send(embed=embed)

        self.delete_eval_job(ctx.author.id)
    
    @command(name="adminevalstop", aliases = ("aestop", ), description = "Stop existing eval jobs")
    @is_owner()
    async def stop_eval(self, ctx: Context) -> None:
        # Stop existing Eval command
        # Sometimes the output is so long, and Bot will be spamming it

        # Check for existing jobs
        if ctx.author.id not in self.eval_jobs:
            await ctx.send(":x: You don't have any eval jobs at the moment!")
            return
        
        log.debug(f"Stop Admin Eval by {ctx.author}")

        # Delete it
        self.delete_eval_job(ctx.author.id)

        await ctx.send("Canceled all eval jobs!")

    async def _format(self, ctx: Context, code: str, result: str) -> list:
        # Format input and output of Admin Eval Command
        # To list of embed

        result_str = str(result)
        if "```" in result_str:
            result_str.replace("```", "'``")
            result = result_str
        
        results = []

        if len(result_str) > 1000:
            text = ''
            
            for i in result_str:

                text += i
                if len(text) > 1000:
                    results.append(text)
                    text = i
            results.append(text)
        
        embeds = []
        
        embed = await self._base_embed(ctx, code)

        if results != []:
            for i in range(len(results)):
                if i != 0:
                    embed = await self._base_embed(ctx, code)
                name = f"{i}"
                value = f"```python\n\n{results[i]}\n\n\n```"
                embed.add_field(name=name, value=value)
                embeds.append(embed)                
        else:
            embed.add_field(name = f"Output {type(result)}", value=f"```python\n\n{result}\n\n\n```")
            embeds.append(embed)
        
        return embeds
    
    async def _base_embed(self, ctx: Context, code: str) -> Embed:
        # Get base embed of Admin Eval command
        embed = Embed(
            title = "Evaluate Command",
            description = f"Run by {ctx.author.mention}" ,
            colour = Color.magenta(),
            timestamp = ctx.message.created_at
        )
        embed.add_field(name="Input:", value=f"```python\n\n{code}\n\n\n```", inline=False)
        return embed


    @command(name = "reload")
    @is_owner()
    async def reload(self, ctx: Context, *, files: str) -> None:
        # Reload bot Extensions

        m = await ctx.send("Reloading...")

        reload = "Succesful!"

        if "exts." not in files:
            files = f"exts.{files}"

        try:
            self.bot.reload_extension(files)
        except Exception as e:
            reload = e
        await m.edit(content=reload)
    
    @command(name = "reloadall")
    @is_owner()
    async def _reload(self, ctx: Context) -> None:
        # Reload ALL bot Extensions

        embed = Embed(
            title = "Reload All Extensions",
            color = Color.magenta()
        )

        extensions = set(EXTENSIONS)

        for i in extensions:
            v = "Succesful!"
            try:
                self.bot.reload_extension(i)
            except:
                v = "Couldn't loaded"

            embed.add_field(name = i, value = v)
        await ctx.send(embed=embed)



def setup(bot: Bot) -> None:
    bot.add_cog(AdminCommands(bot))