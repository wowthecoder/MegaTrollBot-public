import discord
from discord.ext import commands
from random import randint
import youtube_audio_dl
import reddit_dl
import googlesearch
import ctypes
import ctypes.util
from googletrans import Translator
import json

class Fun(commands.Cog):
    description = "" #description for this category
    quotes = []
    flash_quotes = []
    puns = []
    gtrans_langs = {}

    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()
        file = open("gtrans_languages.json", encoding="utf-8")
        Fun.gtrans_langs = json.load(file)
    
    @commands.command(name="search", brief="-mtb search <query>", description="Handy tool to help you search up anything!")
    async def search(self, ctx, term, *more_terms):
        try: 
            query = term
            for t in more_terms:
                query += (" " + t)
            res = googlesearch.search(query, tld="com", num=1, stop=1, pause=0.5)
            url = next(res)
            await ctx.send("Here you go: " + url)
        except Exception as e:
            print(e)
            await ctx.send("I am busy now, please try again later.")

    @commands.command(name="quote", brief="-mtb quote", description="Random quotes from random people to keep you motivated(I hope).")
    async def quote(self, ctx):
        y = randint(0, len(Fun.quotes)-1)
        sentence = Fun.quotes[y]
        sentence = sentence.replace("“", "\"")
        sentence = sentence.replace("”", "\"")
        str_arr = sentence.split("\"")
        q = str_arr[1]
        author = str_arr[-1][2:] #[2:] is used to remove the dash
        quote_embed = discord.Embed(
            title=author,
            description=q,
            color=discord.Color.orange(),
        )
        quote_embed.set_footer(text="Quote requested by: {}".format(ctx.author.display_name))
        await ctx.send(embed=quote_embed)
        #await ctx.send(q + "\n" + "**" + author + "**")

    @commands.command(name="flashquote", brief="-mtb flashquote", description="Generates a random quote from the CW Flash TV show. Go watch it people, it's nice!")
    async def flashquote(self, ctx):
        x = randint(0, len(Fun.flash_quotes)-1)
        sentence = Fun.flash_quotes[x]
        sentence = sentence.replace("“", "\"")
        sentence = sentence.replace("”", "\"")
        str_arr = sentence.split("\"")
        q = str_arr[1]
        author = str_arr[-1][2:]
        quote_embed = discord.Embed(
            title=author,
            description=q,
            color=discord.Color.orange(),
        )
        quote_embed.set_footer(text="Quote requested by: {}".format(ctx.author.display_name))
        await ctx.send(embed=quote_embed)
        #await ctx.send(q + "\n" + "**" + author + "**")

    @commands.command(name="meme", brief="-mtb meme", description="Generates random memes from Reddit!")
    async def meme(self, ctx):
        async with ctx.typing():
            meme_info = await reddit_dl.Reddit_DL.find_post_from_subreddit("memes")
            meme_embed = discord.Embed(
            title=meme_info[0],
            url="https://www.reddit.com/" + meme_info[1],
            color=discord.Color.purple(),
        )
        if meme_info[2].endswith((".jpg", ".png", ".gif")):
            meme_embed.set_image(url=meme_info[2])
        meme_embed.set_footer(text=f"👍 {meme_info[3]} 💬 {meme_info[4]}")
        await ctx.send(embed=meme_embed)

    @commands.command(name="pun", brief="-mtb pun", description="Generates a random pun!")
    async def pun(self, ctx):
        choice = randint(1,4)
        if choice < 4:
            x = randint(0, len(Fun.puns)-1)
            await ctx.send(Fun.puns[x])
        else:
            async with ctx.typing():
                pun_info = await reddit_dl.Reddit_DL.find_post_from_subreddit("puns")
            pun_embed = discord.Embed(
                title=pun_info[0],
                url="https://www.reddit.com/" + pun_info[1],
                color=discord.Color.purple(),
            )
            if pun_info[2].endswith((".jpg", ".png", ".gif")):
                pun_embed.set_image(url=pun_info[2])
            pun_embed.set_footer(text=f"👍 {pun_info[3]} 💬 {pun_info[4]}")
            await ctx.send(embed=pun_embed)

    @commands.command(name="video", brief="-mtb video <query>/<link>", description="Outputs a link redirecting to the video.\nSurprise!")
    async def video(self, ctx, query, *words):
        for w in words:
            query += (" " + w)
        async with ctx.typing():
            video_info = await youtube_audio_dl.YTDLSource.fun_video(query, loop=self.bot.loop)
        video_box = discord.Embed(
            title=video_info[1],
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            description="***Click on the title above^ to go to the video***\n\n" + video_info[2],
        )
        video_box.set_image(url=f"https://img.youtube.com/vi/{video_info[0]}/0.jpg")
        await ctx.send(embed=video_box)
    
    @commands.command(name="sendmsg", brief="-mtb sendmsg <@user> <message>", description="Sends the specified user a message. Lovely surprise!")
    async def sendmsg(self, ctx, user=None, *, message=None):
        if user is None:
            await ctx.send("Well, who you want me to send the message to?")
        elif message is None:
            await ctx.send("What is the message you are sending?")
        else: 
            if isinstance(user, str) and user.isnumeric():
                user = await self.bot.fetch_user(int(user))
                print(user)
            color_code = randint(0, 0xffffff)
            msg_embed = discord.Embed(color=color_code)
            msg_embed.add_field(name=f"{ctx.author} sent you:", value=f"{message}")
            await user.send(embed=msg_embed)
            
    @commands.command(name="translate", brief="-mtb translate <message>", description="Translate a message of any language to english. Handy tool isn't it?")
    async def translate(self, ctx, *, msg:str):
        if len(msg) >= 5000:
            ctx.send("Hey I can't translate a message that long, please summarise what you wanna say")
        async with ctx.typing():
            translation = self.translator.translate(msg)
            translated_text = translation.text
            if translation.src in Fun.gtrans_langs:
                source_lang = Fun.gtrans_langs[translation.src]["name"]
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
    
    @commands.Cog.listener()
    async def on_ready(self):
        quote_file = open("quotes.txt", mode="r", encoding="utf-8")
        flash_file = open("flash_quotes.txt", mode="r", encoding="utf-8")
        puns_file = open("Puns.txt", mode="r", encoding="utf-8")
        for line in quote_file:
            if line.strip() != "":
                Fun.quotes.append(line)
        for line in flash_file:
            if line.strip() != "":
                Fun.flash_quotes.append(line)
        for line in puns_file:
            if line.strip() != "":
                Fun.puns.append(line)
        my_cog = self.bot.get_cog("Fun")
        Fun.description = "Bored? Come here!\n{} total commands".format(len(my_cog.get_commands()))
        print("All quotes successfully loaded!")

def setup(bot):
    bot.add_cog(Fun(bot))
