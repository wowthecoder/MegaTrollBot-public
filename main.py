import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="-mtb ")
bot.remove_command("help")
bot.load_extension("cogs.music")
bot.load_extension("cogs.fun")
bot.load_extension("cogs.util")

@bot.event
async def on_ready():
    bot_activity = discord.Game(name="-mtb help | Used in {} servers".format(str(len(bot.guilds))))
    #bot_activity = discord.Activity(type=discord.ActivityType.listening, name="-mtb help")
    await bot.change_presence(activity=bot_activity)
    print('We have logged in as {0.user}'.format(bot))
    for guild in bot.guilds:
        print(guild.name)
'''
@bot.event
async def on_message(message):
    print(message.guild.name + " -- " + str(message.author) + " : " + message.content)
    if str(message.author) == "The Flash#6266" or str(message.author) == "Charlotte* Frosty XS Cappucino#3653":
        await message.channel.send("你哥哥在看着你！ :smiling_imp:")
'''
    
bot.run("Your bot token here")
