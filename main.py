import discord
from discord.ext import commands
from discord_components import DiscordComponents
import json

def get_prefix(bot, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]
    #to return the default prefix if the guild somehow doesnt exist in the file
    #return prefixes.get(str(message.guild.id), "-mtb ")

intents = discord.Intents().default()
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command("help")
bot.load_extension("cogs.music")
bot.load_extension("cogs.fun")
bot.load_extension("cogs.games")
bot.load_extension("cogs.util")
bot.load_extension("cogs.moderation")

@bot.event
async def on_ready():
    bot_activity = discord.Game(name="-mtb help | Used in {} servers".format(str(len(bot.guilds))))
    #bot_activity = discord.Activity(type=discord.ActivityType.listening, name="-mtb help")
    await bot.change_presence(activity=bot_activity)
    DiscordComponents(bot)
    print('We have logged in as {0.user}'.format(bot))
    #Set default prefix
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    prefixes_edited = False
    for guild in bot.guilds:
        print(guild.name, guild.id)
        if str(guild.id) not in prefixes:
            prefixes[str(guild.id)] = "-mtb "
            prefixes_edited = True
    if prefixes_edited:
        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f, indent=4)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Your command is so complex that I can't understand(I am saying that the command doesn't exist you dumb)")

bot.run("Your bot token here")
