import discord
from discord.ext import commands
import pymongo
from bson.objectid import ObjectId
from datetime import datetime, timedelta

class Snipe(commands.Cog):
    description = ""
    CONNECTION_STRING = "connection string"
    client, db, user_coll= None, None, None
    
    def __init__(self, bot):
        self.bot = bot
        Snipe.client = pymongo.MongoClient(Snipe.CONNECTION_STRING)
        Snipe.db = Snipe.client.mtbDatabase
        Snipe.user_coll = Snipe.db.SnipeUser
    '''    
    @commands.command(name="snipe", brief="snipe [#channel-name] [index of message]", description="The channel default to the current text channel and the index ")
    async def snipe():
        Snipe.server_doc = 
    '''
    @commands.command(name="snipeuser", aliases=["snipeu"], brief="snipeuser <@user> [index]", description="Snipes the last deleted messages of the user in the current server. Index defaults to 1 and max is 5.")
    async def snipeuser(self, ctx, user: discord.Member = None, index: int = 1):
        if user is None:
            await ctx.send("Please provide me a user to snipe.")
            return
        if index > 5:
            await ctx.send("Sorry I can't snipe a message that far back.")
            return
        user_doc = Snipe.user_coll.find_one("user"+str(user.id))
        if user_doc is None or str(ctx.guild.id) not in user_doc:
            await ctx.send("The specified user has no deleted messages in this server.")
            return
        if index > len(user_doc[str(ctx.guild.id)]):
            await ctx.send("That index does not exist for this user.")
            return
        msg_data = user_doc[str(ctx.guild.id)][len(user_doc[str(ctx.guild.id)]) - index]
        time_passed = datetime.now() - msg_data['send_time']
        snipe_box = discord.Embed(
            title = f"Message sent on {msg_data['send_time'].strftime('%I%M%p')}",
            description = msg_data["message_content"],
            color = discord.Color.red(),
        )
        snipe_box.set_author(name=f"Message deleted by {msg_data['author_name']+'#'+msg_data['author_discrim']}", icon_url=msg_data["author_avatar_url"])
        snipe_box.set_footer(text=f"Sniped by {ctx.author}")
        await ctx.send(embed=snipe_box)
        
    @snipeuser.error
    async def snipeuser_error(self, ctx, error):
        print(error)
    
    @commands.command(name="resetsnipeusers", aliases=["rsnipeu"], brief="rsnipeu <@user>/all", description="This command is only for bot developers.")
    @commands.is_owner()
    async def resetsnipeusers(self, ctx, *param):
        if len(param) == 1 and param[0] == "all":
            Snipe.user_coll.delete_many({})
        else: #user tags
            for arg in param: #for each user
                converter = commands.MemberConverter()
                user = await converter.convert(ctx, arg)
                Snipe.user_coll.delete_one({"_id": "user"+str(user.id)})
        await ctx.send("Ok, done boss.")
        
    @resetsnipeusers.error
    async def resetsnipeusers_error(self, ctx, error):
        print(error)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        msg_data = {
            "author_name": message.author.name,
            "author_discrim": message.author.discriminator,
            "author_avatar_url": str(message.author.avatar_url),
            "send_time": message.created_at,
            "message_content": message.content,
            "message_channel": message.channel.name,
        }
        user_doc = Snipe.user_coll.find_one("user"+str(message.author.id))
        if user_doc is None: #if the document for that user does not exist
            user_doc = {"_id": "user"+str(message.author.id),
                        str(message.guild.id): [msg_data]}
            Snipe.user_coll.insert_one(user_doc)
        elif str(message.guild.id) not in user_doc:
            Snipe.user_coll.update_one({"_id": "user"+str(message.author.id)}, {"$set": {str(message.guild.id): [msg_data]}})
        elif len(user_doc[str(message.guild.id)]) < 5:
            Snipe.user_coll.update_one({"_id": "user"+str(message.author.id)}, {"$push": {str(message.guild.id): msg_data}})
            user_doc = Snipe.user_coll.find_one("user"+str(message.author.id))

    @commands.Cog.listener()
    async def on_ready(self):
        my_cog = self.bot.get_cog("Snipe")
        Snipe.description = "Your friend just sent some embarrassing message but quickly deleted it? Don't worry, I got you covered. Use this tool to expose them! MUAHAHAHA\n`{} total commands`".format(len(my_cog.get_commands()))

def setup(bot):
    bot.add_cog(Snipe(bot))