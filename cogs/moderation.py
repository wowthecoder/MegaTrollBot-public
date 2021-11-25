import discord
from discord.ext import commands, tasks
from datetime import date, datetime
import json
import pymongo
from bson.objectid import ObjectId

class Moderation(commands.Cog):
    description = ""
    servermute_list = []
    CONNECTION_STRING = "connection string"
    client, db, general, prefixes = None, None, None, None
    
    def __init__(self, bot):
        self.bot = bot
        self.countdown.start()
        #Get the prefixes
        Moderation.client = pymongo.MongoClient(Moderation.CONNECTION_STRING)
        Moderation.db = Moderation.client.mtbDatabase
        Moderation.general = Moderation.db.general
        Moderation.prefixes = Moderation.general.find_one(ObjectId("617bd86efd5cdcd0c9dd7020"))
        
    @commands.command(name="addrole", aliases=["ar"], brief="addrole <@user> <role name>", description="Duh, as you can see from the name of the command, I will add the specified role to the user. Do you really have to ask?")
    @commands.check_any(commands.has_permissions(manage_roles=True), commands.is_owner())
    async def addrole(self, ctx, user: discord.Member, *, role_name):
        try:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role == None:
                await ctx.send("Bruh that role does not exist yet.(Or you spelled the role name wrongly HAHAHA)")
            else:    
                await user.add_roles(role)
                await ctx.send("Beep bop, done!")
        except discord.Forbidden:
            bot_member = ctx.guild.get_member(self.bot.user.id) 
            highest_role = discord.utils.find(lambda role: role in bot_member.roles, reversed(bot_member.roles))
            await ctx.send(f"I cannot remove the role you specified because my highest role is below the role you want to remove. Please edit the role hierarchy in Server Settings and retry.\n**My highest role:** {highest_role.name} (pos {highest_role.position})\n**The role you want to assign:** {role.name} (pos {role.position})")
    
    @addrole.error
    async def addrole_error(self, ctx, error):
        print(error)
        if isinstance(error, commands.UserInputError):
            await ctx.send(f"It's simple really. You need to type: `{Moderation.prefixes[str(ctx.guild.id)]}addrole <@user> <role name>`, where `<@user>` is the member you want to give the role to, and `<role name>` is the **NAME** of the role you want to give(It must already exist in the server).\nRemember to spell the role name correctly and separate the terms with a space.")
        
    @commands.command(name="removerole", aliases=["rr"], brief="removerole <@user> <role name>", description="Duh, as you can see from the name of the command, I will remove the specified role from the user. Do you really have to ask?")
    @commands.check_any(commands.has_permissions(manage_roles=True), commands.is_owner())
    async def removerole(self, ctx, user: discord.Member, *, role_name):
        try:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role == None:
                await ctx.send("Bruh the role doesn't even exist yet. I can't remove nothing, dummy.\n(Or maybe you just spelled the role name wrong)")
            elif role not in user.roles:
                await ctx.send("You don't have to remove that role from the user because the user doesn't even have that role.")
            else:
                await user.remove_roles(role)
                await ctx.send("Beep bop, done!")
        except discord.Forbidden:
            bot_member = ctx.guild.get_member(self.bot.user.id) 
            highest_role = discord.utils.find(lambda role: role in bot_member.roles, reversed(bot_member.roles))
            await ctx.send(f"I cannot remove the role you specified because my highest role is below the role you want to remove. Please edit the role hierarchy in Server Settings and retry.\n**My highest role:** {highest_role.name} (pos {highest_role.position})\n**The role you want to remove:** {role.name} (pos {role.position})")
    
    @removerole.error
    async def removerole_error(self, ctx, error):
        print(error)
        if isinstance(error, commands.UserInputError):
            await ctx.send(f"It's simple really. You need to type: `{Moderation.prefixes[str(ctx.guild.id)]}removerole <@user> <role name>`, where `<@user>` is the member you want to remove the role from, and `<role name>` is the **NAME** of the role you want to remove(It must already be assigned to the user).\nRemember to spell the role name correctly and separate the terms with a space.")
    
    async def convert_time_str(self, time: int):
        if time < 60:
            return str(time)+"s"
        elif time < 3600: 
            mins = int(time // 60)
            secs = int(time % 60)
            return f"{mins}m {secs}s"
        elif time < 86400:
            hours = int(time // 3600)
            mins = int((time % 3600) // 60) #omit seconds
            return f"{hours}h {mins}m"
        else:
            days = int(time // 86400)
            hours = int((time % 86400) // 3600)
            return f"{days}d {hours}h"
    
    @commands.command(name="servermute", aliases=["sm"], brief="servermute <@user> [duration in seconds]", description="Temporarily stops the user from sending messages in all text channels.\nThe default duration is 10s.\nOnly server administrators can do this!")
    @commands.check_any(commands.has_permissions(administrator=True), commands.is_owner()) #If single function, use @commands.check()
    async def servermute(self, ctx, user: discord.Member, duration: int=10):
        if user.id == ctx.message.author.id:
            await ctx.send("BRO why are you even trying to mute yourself HAHAHAHAHAHAHA")
            return
        if user.id == 484673336534892546: #LOL gluck trying to mute the bot owner
            await ctx.send("Do you even know who you are trying to mute? You are trying to mute the **BOT OWNER** himself!!\nDo you really think I will betray my creator? The answer is a huge __**NO**__")
            return
        muted_role = discord.utils.get(ctx.guild.roles, name="Server Muted")
        if muted_role == None:
            muted_role = await ctx.guild.create_role(name="Server Muted", colour=discord.Color.red())
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)
        if duration > 1209600:
            await ctx.send("Nope I won't let you mute someone for more than 14 days.")
            return 
        #await muted_role.edit(position=len(ctx.guild.roles)-2)
        Moderation.servermute_list.append({"user-id": user.id, "server-id": ctx.guild.id, "start-time": datetime.now(), "duration": duration})
        duration_str = await self.convert_time_str(duration)
        await user.add_roles(muted_role)
        await ctx.send(f"Ok, you muted {user} for {duration_str}.")
        await user.send(f"You are muted in {ctx.guild} for {duration_str} by {ctx.message.author}.")
        
    @commands.command(name="mute", brief="mute <@user> [duration in seconds]", description="Temporarily mute someone in the current text channel. Default duration is 10 seconds.\nTime to SHUT UP!")
    @commands.check_any(commands.has_permissions(administrator=True), commands.is_owner())
    async def mute(self, ctx, user: discord.Member, duration: int=10):
        if user.id == ctx.message.author.id:
            await ctx.send("BRO why are you even trying to mute yourself HAHAHAHAHAHAHA")
            return
        if user.id == 484673336534892546: #LOL gluck trying to mute the bot owner
            await ctx.send("Do you even know who you are trying to mute? You are trying to mute the **BOT OWNER** himself!!\nDo you really think I will betray my creator? The answer is a huge __**NO**__")
            return
        if duration > 1209600:
            await ctx.send("Nope I won't let you mute someone for more than 14 days.")
            return
        await ctx.channel.set_permissions(user, send_messages=False)
        await ctx.send(f"Ok, you muted {user} in {ctx.channel.mention} for {duration_str}")
        await user.send(f"You are muted in text channel {ctx.channel.name} of the server {ctx.guild} for {duration_str} by {ctx.message.author}.")
        '''
        STILL IN DEVELOPMENT
        '''
        
    @commands.command(name="unmute", brief="unmute <@user>", description="Unmutes the user in all accessible text channels.")
    @commands.check_any(commands.has_permissions(administrator=True), commands.is_owner())
    async def unmute(self, ctx, user: discord.Member):
        await ctx.send("still in development.")
    
    @commands.command(name="purge", brief="purge [number of messages] [#channel]", description="Deletes the specified number of messages in the stated text channel.\nDefault text channel is the current text channel and default number of messages purged is 2(including the command)")
    @commands.check_any(commands.has_permissions(manage_messages=True, read_message_history=True), commands.is_owner())
    async def purge(self, ctx, number: int=None, channel: discord.TextChannel=None):
        if channel is None:
            channel = ctx.message.channel
        if number is None:
            number = 2
        elif number > 100:
            await ctx.send("You can't purge more than 100 messages at once.")
            return
        await channel.purge(limit=number)
        await ctx.send(f"Alright, {number} messages purged.")
    
    @tasks.loop(seconds=1.0)
    async def countdown(self):
        try:
            for i in range(len(Moderation.servermute_list)):
                entry = Moderation.servermute_list[i]
                time_elapsed = (datetime.now() - entry["start-time"]).seconds
                if time_elapsed > entry["duration"]:
                    server = await self.bot.fetch_guild(entry["server-id"])
                    member = await server.fetch_member(entry["user-id"])
                    servermute_role = discord.utils.get(server.roles, name="Server Muted")
                    await member.remove_roles(servermute_role)
                    await member.send(f"You are unmuted in {server}.")
                    del Moderation.servermute_list[i]
        except Exception as e:
            print(e)
                
    @countdown.before_loop
    async def before_countdown(self):
        print('waiting...')
        await self.bot.wait_until_ready()
        
    @commands.Cog.listener()
    async def on_ready(self):
        my_cog = self.bot.get_cog("Moderation")
        Moderation.description = "Some handy commands to help u moderate your server.\n`{} total commands`".format(len(my_cog.get_commands()))
        
def setup(bot):
    bot.add_cog(Moderation(bot))
