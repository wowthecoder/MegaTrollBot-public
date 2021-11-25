import discord
from discord.ext import commands
from discord_components import DiscordComponents
import json
import pymongo
from bson.objectid import ObjectId

CONNECTION_STRING = "connection string"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.mtbDatabase #create a database(like a server/computer) called "mtbDatabase" if it doesn't exist, else fetch the database
general = db.general #create a collection(like a folder) called "general" if it doesn't exist, else fetch the collection

def get_prefix(bot, message):
    try:
        prefixes = general.find_one(ObjectId("617bd86efd5cdcd0c9dd7020"))
        return prefixes[str(message.guild.id)]
        #to return the default prefix if the guild somehow doesnt exist in the file
        #return prefixes.get(str(message.guild.id), "-mtb ")
    except Exception as e: #If server somehow does not exist in file or DM channel
        return "-mtb "

intents = discord.Intents().default()
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command("help")
bot.load_extension("cogs.music")
bot.load_extension("cogs.fun")
bot.load_extension("cogs.games")
bot.load_extension("cogs.util")
bot.load_extension("cogs.moderation")
bot.load_extension("cogs.snipe")

@bot.event
async def on_ready():
    bot_activity = discord.Game(name="-mtb help | Used in {} servers".format(str(len(bot.guilds))))
    #bot_activity = discord.Activity(type=discord.ActivityType.listening, name="-mtb help")
    await bot.change_presence(activity=bot_activity)
    DiscordComponents(bot)
    print('We have logged in as {0.user}'.format(bot))
    #Set default prefix
    prefixes = general.find_one(ObjectId("617bd86efd5cdcd0c9dd7020"))
    for guild in bot.guilds:
        print(guild.name, guild.id)
        if str(guild.id) not in prefixes:
            prefixes[str(guild.id)] = "-mtb "

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Your command is so complex that I can't understand(I am saying that the command doesn't exist you dumb)")

bot.run("bot token")
