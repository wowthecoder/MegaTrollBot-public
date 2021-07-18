import discord
from discord.ext import commands

class Utils(commands.Cog):
    description = ""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", brief="-mtb help [category]/[command]", description="Displays the full lists of commands available for this bot.")
    async def help(self, ctx, *args):
        emojis = {"Music" : ":guitar:",
                  "Fun" : ":zany_face:",
                  "Utils" : ":tools:",
                  }
        if len(args) != 0:
            name = args[0].lower().capitalize()
            for c in self.bot.cogs:
                if name == c:
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
                    categorybox.set_footer(text="type -mtb help <command> for more info on a specific command.\nuse -mtb before each command!")
                    await ctx.send(embed=categorybox)
                    break
                else:
                    for comm in self.bot.get_cog(c).get_commands():
                        if comm.name == name.lower():
                            commandbox = discord.Embed(
                                title=f"-mtb {comm.name} info",
                                description=f"**Description:**\n{comm.description}",
                                color=discord.Color.gold(),
                            )
                            commandbox.add_field(name="How to use:", value=f"`{comm.brief}`", inline=False)
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
        helpbox.add_field(name="Invite", value="MegaTrollBot can be added to as many servers as you want! [Click here to add it to yours.](https://discord.com/api/oauth2/authorize?client_id=852914675493502997&permissions=2184703040&scope=bot) \n\u200b", inline=False)
        for c in self.bot.cogs:
            category = self.bot.get_cog(c)
            helpbox.add_field(name=f"{emojis[c]} {c}\n", value=category.description, inline=False)
        helpbox.set_footer(text="Type -mtb help [command] for more info on a specific command.\nYou can also type -mtb help [category] for more info on a category.")
        await ctx.send(embed=helpbox)
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send("Hello! Thanks for adding me to your server. Have fun!")
                await self.help(channel)
                bot_activity = discord.Game(name="-mtb help | Used in {} servers".format(str(len(bot.guilds))))
                await bot.change_presence(activity=bot_activity)
                break

    @commands.Cog.listener()
    async def on_ready(self):
        my_cog = self.bot.get_cog("Utils")
        Utils.description = "Some utilities to know more about me.\n{} total commands".format(len(my_cog.get_commands()))

def setup(bot):
    bot.add_cog(Utils(bot))
