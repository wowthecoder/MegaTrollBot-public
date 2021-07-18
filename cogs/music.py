import discord
from discord.ext import commands
import os
import youtube_audio_dl
import spotify_player
import ctypes
import ctypes.util
import time
import asyncio
import random

class Music(commands.Cog):
    description = "" #description for this category
    '''
    song_queue = []
    current_track_start_time = 0
    track_duration = 0
    '''

    ffmpeg_options = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        'options': '-vn',
    }

    def __init__(self, bot):
        self.bot = bot
        self.loop_track = False
        self.queue = []
        self.loop_queue = False
        self.queue_index = 0
        self.queue_stopped = False

    async def play_next(self, ctx, *audio_info):
        if self.loop_track == True:
            self.current_track_start_time = time.time()
            bot = self.bot
            audio_url = audio_info[0]
            audio_name = audio_info[1]
            bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            bot_voice_client.play(discord.FFmpegPCMAudio(audio_url, **Music.ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx, audio_url, audio_name), bot.loop))
            await ctx.send("**Looping Song: ** {} :musical_note:".format(audio_name))
        elif not self.queue_stopped: #plays the next song in the queue
            queue = self.queue
            self.queue_index += 1
            i = self.queue_index
            if len(queue) > i:
                self.current_track_start_time = time.time()
                self.track_duration = queue[i]['duration']
                bot = self.bot
                track_url = queue[i]['url']
                track_name = queue[i]['name']
                bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
                bot_voice_client.play(discord.FFmpegPCMAudio(track_url, **Music.ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx, track_url, track_name), bot.loop))
                await ctx.send("**Now playing: ** {} :musical_note:".format(track_name))

    async def join_voice(self, ctx):
        voice_channel = ctx.author.voice.channel
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    
        if bot_voice_client == None and voice_channel != None: #None being the default value if the bot isn't in the voice channel
            bot_voice_client = await voice_channel.connect()
            await ctx.guild.change_voice_state(channel=voice_channel, self_deaf=True)
        elif bot_voice_client.channel != voice_channel: #If the bot isn't in the same voice channel as the user
            await ctx.voice_client.disconnect()
            bot_voice_client = await voice_channel.connect()
            await ctx.guild.change_voice_state(channel=voice_channel, self_deaf=True)
    
    @commands.command(name="join", brief="-mtb join", description="Joins the voice channel that you are currently in. Hooray!")
    async def join(self, ctx):
        try:
            await self.join_voice(ctx)
        except Exception as e:
            print(e)
            await ctx.send("Sorry bro, either an error occurred, or you are not in a voice channel.")        

    @commands.command(name="play", brief="-mtb play <query>/<link>", description="Plays the music you requested or searched in the voice channel. Time to chill!\nIf you already have a song playing, this command will add the song to the queue.\n*Currently only support Youtube and Spotify links.")
    async def play(self, ctx, *, url):
        try:
            await self.join_voice(ctx)

            voice_channel = ctx.author.voice.channel
            bot = self.bot #For some reason I need to add this in front to work
            bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

            searching_msg = await ctx.send(":mag: Searching...")
            spotify_playlist = False
            async with ctx.typing():
                '''
                #download audio(not recommended)
                filename = await audio_downloader.YTDLSource.from_url(url, loop=bot.loop)
                bot_voice_client.play(discord.FFmpegPCMAudio(source=filename), after=lambda x: os.remove(filename))
                '''
                if (url.startswith("https://open.spotify.com/")):
                    if (url.startswith("https://open.spotify.com/track/")):
                        audio_info = await spotify_player.SpotifyDL.from_url(url, loop=bot.loop)
                    elif (url.startswith("https://open.spotify.com/playlist/")):
                        start_time = time.time()
                        audio_info = await spotify_player.SpotifyDL.songs_from_playlist(url, 0, loop=bot.loop)
                        num_of_songs = await spotify_player.SpotifyDL.num_of_songs(url)
                        print(time.time()-start_time)
                        spotify_playlist = True
                    else:
                        ctx.send("Sorry, I can't play the song you requested.")
                else:
                    #stream audio
                    start_time = time.time()
                    audio_info = await youtube_audio_dl.YTDLSource.from_url(url, loop=bot.loop)
                    print("aha", time.time() - start_time)
                await searching_msg.delete()
                
            queue = self.queue
            audio_url = audio_info[0]
            audio_name = audio_info[1]
            if len(queue) >= 300:
                await ctx.send("You can only have a maximum of 300 songs in the queue at a time.")
            else:
                track_info = { 'name' : audio_name, 'url' : audio_url, 'duration' : audio_info[2]}
                queue.append(track_info)
                
            if not bot_voice_client.is_playing():
                self.current_track_start_time = time.time()
                self.track_duration = audio_info[2]
                bot_voice_client.play(discord.FFmpegPCMAudio(audio_url, **Music.ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx, audio_url, audio_name), bot.loop))
                await ctx.send('**Now playing:** {} :musical_note:'.format(audio_name))
            else:
                await ctx.send("**Track queued:** {} :heart_on_fire:".format(audio_name))
            if spotify_playlist:
                for i in range(1, num_of_songs):
                    start_time = time.time()
                    track = await spotify_player.SpotifyDL.songs_from_playlist(url, i, loop=bot.loop)
                    print(i, time.time()-start_time)
                    track_info = { 'name' : track[1], 'url' : track[0], 'duration' : track[2]}
                    self.queue.append(track_info)
                await ctx.send("All songs queued!")
        except Exception as e:
            print(e)
            await ctx.send("Sorry bro, either an error occurred, or you are not in a voice channel.")

    @commands.command(name="pause", brief="-mtb pause", description="Need a break? This command pauses the audio that you are currently playing.")
    async def pause(self, ctx):
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        msg = ctx.message
        if bot_voice_client.is_playing():
            bot_voice_client.pause()
            await msg.add_reaction('⏸')
        else:
            await ctx.send("LOL there's no audio playing now, what are you doing man?")

    @commands.command(name="resume", brief="-mtb resume", description="The break is over, it's time to put the music back on!")
    async def resume(self, ctx):
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        msg = ctx.message
        if bot_voice_client.is_paused():
            bot_voice_client.resume()
            await msg.add_reaction('▶')
        else:
           await ctx.send("No need to resume, Either there is no audio or the audio is already playing.") 

    @commands.command(name="stop", brief="-mtb stop", description="Tired of your friends' silly music? Stop the music anytime!")
    async def stop(self, ctx):
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        msg = ctx.message
        if  bot_voice_client.is_playing():
            self.queue_index = -1
            self.loop_track = False
            self.queue_stopped = True
            bot_voice_client.stop()
            await msg.add_reaction('🛑')
        else:
            await ctx.send("LOL there's no audio playing now, what are you doing man?")

    @commands.command(name="loopsong", brief="-mtb loop", description="Put your favourite tune on loop and revel in the heavenly melody for hours.")
    async def loopsong(self, ctx):
        try:
            self.loop_track = True
            await ctx.message.add_reaction('✌')
            await ctx.send("Loop mode is ON!")
        except Exception as e:
            print(e)
            await ctx.send("You cannot loop nothing, donkey. 0 times Infinity is still 0.")

    @commands.command(name="stoploop", brief="-mtb stoploop", description="Had enough? Stop the loop and give your ears some well-deserved peace.")
    async def stoploop(self, ctx):
        try:
            self.loop_track = False
            await ctx.message.add_reaction('⛔')
            await ctx.send("Loop mode is OFF!")
        except Exception as e:
            print(e)
            await ctx.send("You cannot stop the loop if there is no loop, darling.")

    @commands.command(name="queue", brief="-mtb queue", description="Displays the current song queue")
    async def queue(self, ctx):
        queue_block = "```\n"
        for index, song_info in enumerate(self.queue):
            audio_name = song_info['name']
            audio_duration = song_info['duration']
            minutes = int(audio_duration // 60)
            seconds = audio_duration % 60
            if index == self.queue_index:
                supposed_endtime = self.current_track_start_time + self.track_duration
                time_left_in_sec = supposed_endtime - time.time()
                mins = int(time_left_in_sec // 60)
                sec = round(time_left_in_sec) % 60
                queue_block += "[Current song] ⤵\n"
                queue_block += f"{index+1}) {audio_name}  {mins}min {sec}s left\n"
                queue_block += "[Current song] ⤴\n"
            else:
                queue_block += f"{index+1}) {audio_name}  {minutes}:{seconds}\n"
        if len(self.queue) == 0:
            queue_block += "You have no songs in the queue now, go add some!\n```"
        if len(self.queue) != 0:
            queue_block += "\nThis is the end of the queue.\n```"
        await ctx.send(queue_block)
    
    @commands.command(name="restart", brief="-mtb restart", description="Starts playing from the beginning of the queue.")
    async def restart(self, ctx):
        if len(self.queue) == 0:
            await ctx.send("Don't bother me when you have no songs in the queue, donkey.")
            return
        self.queue_index = -1
        self.loop_track = False
        self.queue_stopped = False
        await self.play_next(ctx)
    
    @commands.command(name="clear", brief="-mtb clear", description="Clears the current song queue.")
    async def clear(self, ctx):
        self.queue.clear()
        await ctx.send("Queue cleared!")
        
    @commands.command(name="jump", brief="-mtb jump <number>", description="Skips to the specified track in the queue.")
    async def jump(self, ctx, pos):
        await ctx.send("Still in development.")
        
    @commands.command(name="skip", brief="-mtb skip", description="Skips to the next song.")
    async def skip(self, ctx):
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        msg = ctx.message
        if bot_voice_client.is_playing():
            self.loop_track = False
            bot_voice_client.stop()
            await ctx.send(":next_track: ***Skipped***")
        else:
            await ctx.send("LOL there's no audio playing now, what are you doing man?")
        
    @commands.command(name="back", brief="-mtb back", description="Skips to the previous song.")
    async def back(self, ctx):
        await ctx.send("Still in development.")
        
    @commands.command(name="remove", brief="-mtb remove <number>", description="Remove the specified track in the queue.")
    async def remove(self, ctx, pos: int):
        await ctx.send("Still in development.")
        
    @commands.command(name="shuffle", brief="-mtb shuffle", description="Shuffles the queue.")
    async def shuffle(self, ctx):
        random.shuffle(self.queue)
        await ctx.send("Queue shuffled!")
        
    @commands.command(name="move", brief="-mtb move <song position in queue> <new position>", description="Moves the specified song to a specific position in the queue.")
    async def move(self, ctx, original_pos, new_pos):
        await ctx.send("Still in development.")
    
    @commands.command(name="loopqueue", brief="-mtb loopqueue", description="Loops the queue. I will play the first song again once the last song is finished playing")
    async def loopqueue(self, ctx):
        await ctx.send("Still in development.")        
    
    @commands.command(name="leave", brief="-mtb leave", description="I don't want to leave, but I have to, doesn't I?\nNever gonna run around and desert you~")
    async def leave(self, ctx):
        try:
            voice_channel = ctx.author.voice.channel
            bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            msg = ctx.message
            if voice_channel == bot_voice_client.channel:
                await ctx.voice_client.disconnect()
                await msg.add_reaction('🏃')
                await self.clear(ctx) #call the clear queue command
            else:
                await ctx.send("Hey! You can't disconnect me from another voice channel.")
        except Exception as e:
            print(e)
            await ctx.send("How am I supposed to disconnect if I am not yet in a voice channel? Aduhai.")

    @commands.command(name="timeleft", brief="-mtb timeleft", description="Displays the time left for the current queue.")
    async def timeleft(self, ctx):
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if bot_voice_client.is_playing():
            total_duration, time_passed = 0, 0
            for index, song in enumerate(self.queue):
                total_duration += song['duration']
                if index < self.queue_index:
                    time_passed += song['duration']
                elif index == self.queue_index:
                    time_passed += round(time.time() - self.current_track_start_time)
            
            time_left_in_sec = total_duration - time_passed
            hours = int(time_left_in_sec // 3600)
            minutes = int((time_left_in_sec % 3600) // 60)
            seconds = time_left_in_sec % 60
            embed_box = discord.Embed(
                color=discord.Color.blue(),
            )
            embed_box.add_field(name="Time left for current queue: ", value=("{hour} {h_word} {minute} {min_word} {sec} {sec_word}".format(hour=hours, h_word="hours" if hours > 1 else "hour", minute=minutes, min_word="minutes" if minutes > 1 else "minute", sec=seconds, sec_word="seconds" if seconds > 1 else "second")))    
            await ctx.send(embed=embed_box)
        else:
            await ctx.send("You are not even playing any music lol")

    #To detect when the bot leaves the voice channel
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        #To detect when a bot leaves a voice channel
        if member == "MegaTrollBot#0395" and before.channel is not None and after.channel is None:
            self.queue.clear()
            #await member.guild.system_channel.send("Queue cleared!")
        
    
    @commands.Cog.listener()
    async def on_ready(self):
        my_cog = self.bot.get_cog("Music")
        Music.description = "Play some music in your voice chat. It's time to rock n roll!\n{} total commands".format(len(my_cog.get_commands()))
        print("Music bot ready to rock n roll!")

def setup(bot):
    bot.add_cog(Music(bot))
