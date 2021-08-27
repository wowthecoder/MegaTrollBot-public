import discord
from discord.ext import commands
from datetime import datetime
from random import randint
from googletrans import Translator
import json
import re

class Utils(commands.Cog):
    description = ""
    gtrans_langs = {}

    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()
        with open("gtrans_languages.json", encoding="utf-8") as file:
            Utils.gtrans_langs = json.load(file)
        with open("prefixes.json", "r") as f:
            self.prefixes = json.load(f)

    @commands.command(name="help", brief="help [category]/[command]", description="Displays the full lists of commands available for this bot.")
    async def help(self, ctx, *args):
        emojis = {"Music" : ":guitar:",
                  "Fun" : ":zany_face:",
                  "Utils" : ":tools:",
                  "Moderation": ":robot:",
                  "Games": ":game_die:"
                  }
        if len(args) != 0:
            name = args[0].lower().capitalize()
            for c in self.bot.cogs:
                if name == c: #The argument is a category name
                    category = self.bot.get_cog(name)
                    command_list = category.get_commands()
                    command_text = ""
                    for comm in command_list:
                        command_text += f"`{comm}`,"
                    categorybox = discord.Embed(
                        title=f"{emojis[name]} {name} Commands",
                        description=command_text[:-1],
                        color=discord.Color.gold(),
                    )                
                    categorybox.set_footer(text=f"type {self.prefixes[str(ctx.guild.id)]}help <command> for more info on a specific command.\nuse -mtb before each command!")
                    await ctx.send(embed=categorybox)
                    break
                else: #The argument is a command name
                    for comm in self.bot.get_cog(c).get_commands():
                        if comm.name == name.lower():
                            commandbox = discord.Embed(
                                title=f"{self.prefixes[str(ctx.guild.id)]}{comm.name} info",
                                description=f"**Description:**\n{comm.description}",
                                color=discord.Color.gold(),
                            )
                            #For aliases
                            aliases = [comm.name]
                            if comm.aliases != None:
                                aliases.extend(comm.aliases)
                            commandbox.add_field(name="Aliases", value=", ".join(aliases), inline=False)
                            commandbox.add_field(name="How to use:", value=f"`{self.prefixes[str(ctx.guild.id)]}{comm.brief}`", inline=False)
                            commandbox.set_footer(text="Usage Syntax: <required> [optional]")
                            await ctx.send(embed=commandbox)
                            return
            else:
                await ctx.send("Bruh that isn't even a legit category or command.")
            return
        
        helpbox = discord.Embed(
            title="MegaTrollBot Command list",
            description="Welcome to MegaTrollBot! I am the most legendary bot ever made on Discord :laughing:.",
            color=discord.Color.gold(),
        )
        helpbox.add_field(name="Invite", value="MegaTrollBot can be added to as many servers as you want! [Click here to add it to yours.](https://discord.com/api/oauth2/authorize?client_id=852914675493502997&permissions=8&scope=bot) \n\u200b", inline=False)
        for c in self.bot.cogs:
            category = self.bot.get_cog(c)
            helpbox.add_field(name=f"{emojis[c]} {c}\n", value=category.description, inline=False)
        helpbox.set_footer(text=f"Type {self.prefixes[str(ctx.guild.id)]}help [command] for more info on a specific command.\nYou can also type {self.prefixes[str(ctx.guild.id)]}help [category] for more info on a category.")
        await ctx.send(embed=helpbox)
     
    @commands.command(name="serverinfo", aliases=["si"], brief="serverinfo", description="Displays some information about the current server.")
    async def serverinfo(self, ctx):
        guild = ctx.message.guild
        infobox = discord.Embed(
            title = f"Server name: {guild.name}",
            color = discord.Color.blue(),
        )
        owner = await self.bot.fetch_user(guild.owner_id)
        infobox.set_thumbnail(url=guild.icon_url)
        infobox.add_field(name="Server ID", value=guild.id, inline=False)
        infobox.add_field(name="Server owner", value=owner, inline=False)
        infobox.add_field(name="Created on", value=guild.created_at.strftime("%A, %d %b %Y at %I:%M %p UTC"), inline=False)
        infobox.add_field(name="Location", value=guild.region)
        infobox.add_field(name="Channels", value=f"**{len(guild.categories)}** categories, **{len(guild.channels)-len(guild.categories)}** channels: **{len(guild.text_channels)}** text channels and **{len(guild.voice_channels)}** voice channels", inline=False)
        infobox.add_field(name="Member count", value=f"{guild.member_count} members", inline=False)
        infobox.add_field(name="Roles", value=f"{len(guild.roles)} roles available")
        infobox.add_field(name="Verification level", value=guild.verification_level)
        await ctx.send(embed=infobox)
        
    @commands.command(name="channelinfo", aliases=["ci"], brief="channelinfo [#channel-name]", description="Displays some information about the specified text channel. The default text channel is the current channel.")
    async def channelinfo(self, ctx, channel: discord.TextChannel=None):
        if channel is None:
            channel = ctx.message.channel
        infobox = discord.Embed(
            title = f"Channel name: {channel.name}",
            color = discord.Color.blue(),
        )
        member_list = channel.members
        channel_owner = ctx.message.guild.owner #default channel owner
        for member in member_list:
            check = channel.overwrites_for(member).manage_channels
            if check == True:
                channel_owner = member
                break
        infobox.set_thumbnail(url=channel_owner.avatar_url)
        infobox.add_field(name="Channel ID", value=channel.id, inline=False)
        infobox.add_field(name="Channel owner", value=f"<@!{channel_owner.id}>", inline=False)
        member_list = [f"<@!{member.id}>" for member in member_list if member.bot == False]
        member_list_str = ', '.join(member_list)
        infobox.add_field(name="No. of members in the channel", value=len(member_list), inline=False)
        infobox.add_field(name="Members", value=member_list_str, inline=False)
        await ctx.send(embed=infobox)
    
    @channelinfo.error
    async def channelinfo_error(self, ctx, error):
        print(error) 
        if isinstance(error, commands.BadArgument):
            await ctx.send("Either leave the channel argument blank or give me a valid text channel, not some random junk text")
            
    @commands.command(name="userinfo", aliases=["ui"], brief="userinfo [@user]", description="Displays some information about the specified user. The default is yourself. Stalking?")
    async def userinfo(self, ctx, user: discord.Member=None):
        if user is None:
            user = ctx.message.author
        color_code = randint(0, 0xffffff)
        infobox = discord.Embed(
            title = f"Username: {user}",
            description = f"Nickname: {user.nick}",
            color = color_code,
        )
        infobox.set_thumbnail(url=user.avatar_url) 
        infobox.add_field(name="Joined Discord on", value=user.created_at.strftime(f"%a, %d %b %Y\n({(datetime.now()-user.created_at).days} days ago)"))
        infobox.add_field(name="Joined server on", value=user.joined_at.strftime(f"%a, %d %b %Y\n({(datetime.now()-user.joined_at).days} days ago)"))
        user_roles = [role.mention for role in user.roles]
        infobox.add_field(name="Roles", value=', '.join(user_roles), inline=False)
        infobox.set_footer(text=f"ID: {user.id}")
        await ctx.send(embed=infobox)
    
    @userinfo.error
    async def userinfo_error(self, ctx, error):
        print(error) 
        if isinstance(error, commands.BadArgument):
            await ctx.send("Either leave the user argument blank or give me a valid user, not some random junk text")
            
    @commands.command(name="autoreact", brief="-mtb autoreact <@user> <emojis(max 3)>", description="Sets up an autoreact function for the specified user. The bot will react with the specified emojis when certain words appear in messages. The emojis must come from this server.")
    async def autoreact(self, ctx, user: discord.Member, *, emojis):
        ctx.send("I know you are excited for this, but unfortunately this function is still in development.")
        
    @commands.command(name="translate", brief="translate <message>", description="Translate a message of any language to english. Handy tool isn't it?")
    async def translate(self, ctx, *, msg:str):
        if len(msg) >= 5000:
            ctx.send("Hey I can't translate a message that long, please summarise what you wanna say")
        async with ctx.typing():
            translation = self.translator.translate(msg)
            translated_text = translation.text
            if translation.src in Utils.gtrans_langs:
                source_lang = Utils.gtrans_langs[translation.src]["name"]
            else:
                print("Unknown language code:", translation.src)
                source_lang = "Unknown"
        translate_box = discord.Embed(
            title="Google Translate",
            color=discord.Color.blue(),
        )
        translate_box.add_field(name=f"Source language: {source_lang}", value=translated_text)
        translate_box.set_footer(text="Yay it works")
        await ctx.send(embed=translate_box)
        
    @translate.error
    async def translate_error(self, ctx, error):
        print(error)
        
    @commands.command(name="prefix", brief="prefix <new prefix>", description="Set a custom prefix for me in your server.\nPrefix must be less than 10 characters long!\nIf you want a space after the prefix, enclose the new prefix in double quotes,eg.\"lol \"")
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, custom_prefix):
        if len(custom_prefix) > 10:
            await ctx.send("Hey don't give me a long ass prefix, keep it under 10 characters please.")
            return
        if re.match(r"\"[A-Za-z\s]+\"", custom_prefix):
            custom_prefix = re.search(r"\"[A-Za-z\s]+\"", custom_prefix).group(1)
        self.prefixes[str(ctx.guild.id)] = custom_prefix
        with open("prefixes.json", "w") as f:
            json.dump(self.prefixes, f, indent=4)
        #Change nickname of bot
        bot_member = await ctx.guild.fetch_member(self.bot.user.id)
        bot_name = bot_member.display_name
        if bot_name.startswith("[") and "]" in bot_name:
            close_bracket_pos = bot_name.index("]")
            bot_name = bot_name[(close_bracket_pos+1):]
        await bot_member.edit(nick=f"[{custom_prefix}]{bot_name}")
        await ctx.send(f"Prefix for this server changed to **\"{custom_prefix}\"**\nEg. {custom_prefix}help")
    
    @prefix.error
    async def prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Sorry, only server admins can change my prefix, and sadly you are not one.")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send("Hello! Thanks for adding me to your server. Have fun!")
                await self.help(channel)
                bot_activity = discord.Game(name="-mtb help | Used in {} servers".format(str(len(self.bot.guilds))))
                await self.bot.change_presence(activity=bot_activity)
                break
        #Add default prefix to file
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        prefixes[str(guild.id)] = "-mtb "
        with open("prefixes.json", "r") as f:
            prefixes = json.dump(prefixes, f, indent=4)
            
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        #Remove entry from prefixes file
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)
        prefixes.pop(str(guild.id))
        with open("prefixes.json", "w") as f:
            prefixes = json.dump(prefixes, f, indent=4)

    @commands.Cog.listener()
    async def on_ready(self):
        my_cog = self.bot.get_cog("Utils")
        Utils.description = "Some utilities to know more about me and the server.\n`{} total commands`".format(len(my_cog.get_commands()))

def setup(bot):
    bot.add_cog(Utils(bot))
