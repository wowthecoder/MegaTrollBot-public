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
from discord_components import Button, ButtonStyle, InteractionType

class Music(commands.Cog):
    description = "" #description for this category

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
        self.queue_page = 1

    async def play_next(self, ctx):
        if self.loop_track == True:
            self.current_track_start_time = time.time()
            bot = self.bot
            queue = self.queue 
            audio_url = queue[self.queue_index]["url"]
            audio_name = queue[self.queue_index]["name"]
            audio_artist = queue[self.queue_index]["artist"]
            audio_ytid = queue[self.queue_index]["ytid"]
            bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            bot_voice_client.play(discord.FFmpegPCMAudio(audio_url, **Music.ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), bot.loop))
            music_infobox = discord.Embed(
                    title=f":musical_note: {audio_name}",
                    description=f"[{audio_name} by {audio_artist}](https://youtu.be/{audio_ytid})",
                    color=discord.Color.green(),
            )
            music_infobox.set_thumbnail(url=f"https://i.ytimg.com/vi/{audio_ytid}/hqdefault.jpg")
            music_infobox.set_footer(text=f"Voice channel: {bot_voice_client.channel.name}")
            await ctx.send(content=":arrows_counterclockwise: **LOOPING SONG**", embed=music_infobox)
        elif not self.queue_stopped: #plays the next song in the queue
            queue = self.queue
            self.queue_index += 1
            if self.queue_index >= len(queue) and self.loop_queue is True:
                self.queue_index = 0
            i = self.queue_index
            if i < len(queue):
                self.current_track_start_time = time.time()
                self.track_duration = queue[i]['duration']
                bot = self.bot
                track_url = queue[i]['url']
                track_name = queue[i]['name']
                track_artist = queue[i]['artist']
                track_ytid = queue[i]['ytid']
                bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
                bot_voice_client.play(discord.FFmpegPCMAudio(track_url, **Music.ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), bot.loop))
                music_infobox = discord.Embed(
                    title=f":musical_note: {track_name}",
                    description=f"[{track_name} by {track_artist}](https://youtu.be/{track_ytid})",
                    color=discord.Color.green(),
                )
                music_infobox.set_thumbnail(url=f"https://i.ytimg.com/vi/{track_ytid}/hqdefault.jpg")
                music_infobox.set_footer(text=f"Voice channel: {bot_voice_client.channel.name}")
                await ctx.send(content=":loudspeaker: **NOW PLAYING**", embed=music_infobox)

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
    
    @commands.command(name="join", brief="join", description="Joins the voice channel that you are currently in. Hooray!")
    async def join(self, ctx):
        try:
            await self.join_voice(ctx)
        except Exception as e:
            print(e)
            await ctx.send("Sorry bro, either an error occurred, or you are not in a voice channel.")        

    @commands.command(name="play", brief="play <query>/<link>", description="Plays the music you requested or searched in the voice channel. Time to chill!\nIf you already have a song playing, this command will add the song to the queue.\n*Currently only support Youtube and Spotify links.")
    async def play(self, ctx, *, url):
        try:
            await self.join_voice(ctx)

            voice_channel = ctx.author.voice.channel
            bot = self.bot #For some reason I need to add this in front to work
            bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

            searching_msg = await ctx.send(":mag: Searching...")
            spotify_playlist = False
            youtube_playlist = False
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
                elif url.startswith("https://www.youtube.com/playlist"):
                    #First song
                    audio_info = await youtube_audio_dl.YTDLSource.song_from_playlist(url, 1, loop=bot.loop) 
                    youtube_playlist = True
                else:
                    #stream audio
                    start_time = time.time()
                    audio_info = await youtube_audio_dl.YTDLSource.from_url(url, loop=bot.loop)
                    print("aha", time.time() - start_time)
                await searching_msg.delete()
                
            queue = self.queue
            audio_url = audio_info[0]
            audio_name = audio_info[1]
            audio_artist = audio_info[2]
            audio_ytid = audio_info[3]
            audio_duration = audio_info[4]
            if len(queue) >= 300:
                await ctx.send("You can only have a maximum of 300 songs in the queue at a time.")
            else:
                track_info = { 'name' : audio_name, 'artist': audio_artist, 'url' : audio_url, 'ytid': audio_ytid, 'duration' : audio_duration}
                queue.append(track_info)
                
            if not bot_voice_client.is_playing():
                self.queue_stopped = False
                self.current_track_start_time = time.time()
                self.track_duration = audio_duration
                bot_voice_client.play(discord.FFmpegPCMAudio(audio_url, **Music.ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), bot.loop))
                music_infobox = discord.Embed(
                    title=f":musical_note: {audio_name}",
                    description=f"[{audio_name} by {audio_artist}](https://youtu.be/{audio_ytid})",
                    color=discord.Color.green(),
                )
                music_infobox.set_thumbnail(url=f"https://i.ytimg.com/vi/{audio_ytid}/hqdefault.jpg")
                music_infobox.set_footer(text=f"Voice channel: {voice_channel.name}")
                await ctx.send(content=":loudspeaker: **NOW PLAYING**", embed=music_infobox)
            else:
                await ctx.send("**TRACK QUEUED:** {} :heart_on_fire:".format(audio_name))
            if spotify_playlist:
                for i in range(1, num_of_songs):
                    start_time = time.time()
                    track = await spotify_player.SpotifyDL.songs_from_playlist(url, i, loop=bot.loop)
                    print(i, time.time()-start_time)
                    track_info = { 'name' : track[1], 'url' : track[0], 'artist': track[2], 'ytid': track[3], 'duration' : track[4]}
                    self.queue.append(track_info)
                await ctx.send("All songs queued!")
            elif youtube_playlist:
                i = 2
                while True:
                    start_time = time.time()
                    track = await youtube_audio_dl.YTDLSource.song_from_playlist(url, i, loop=bot.loop)
                    print(i, time.time()-start_time)
                    if track is False:
                        break
                    track_info = {'name': track[1], 'url': track[0], 'artist': track[2], 'ytid': track[3], 'duration': track[4]}
                    self.queue.append(track_info)
                    i += 1
                await ctx.send("All songs queued!")
        except Exception as e:
            print(e)
            await ctx.send("Sorry bro, either an error occurred, or you are not in a voice channel.")

    def is_in_same_vc(ctx):
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if ctx.author.voice.channel is not None and bot_voice_client.channel == ctx.author.voice.channel:
            return True
        else:
            return False

    @commands.command(name="pause", brief="pause", description="Need a break? This command pauses the audio that you are currently playing.")
    @commands.check(is_in_same_vc)
    async def pause(self, ctx):
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        msg = ctx.message
        if bot_voice_client.is_playing():
            bot_voice_client.pause()
            await msg.add_reaction('⏸')
        else:
            await ctx.send("LOL there's no audio playing now, what are you doing man?")

    @commands.command(name="resume", brief="resume", description="The break is over, it's time to put the music back on!")
    @commands.check(is_in_same_vc)
    async def resume(self, ctx):
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        msg = ctx.message
        if bot_voice_client.is_paused():
            bot_voice_client.resume()
            await msg.add_reaction('▶')
        else:
           await ctx.send("No need to resume, Either there is no audio or the audio is already playing.") 

    @commands.command(name="stop", brief="stop", description="Tired of your friends' silly music? Stop the music anytime!\nAlso stops looping the queue.")
    @commands.check(is_in_same_vc)
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

    @commands.command(name="loopsong", brief="loop", description="Put your favourite tune on loop and revel in the heavenly melody for hours.")
    @commands.check(is_in_same_vc)
    async def loopsong(self, ctx):
        try:
            self.loop_track = True
            await ctx.message.add_reaction('✌')
            await ctx.send("Loop mode is ON!")
        except Exception as e:
            print(e)
            await ctx.send("You cannot loop nothing, donkey. 0 times Infinity is still 0.")

    @commands.command(name="stoploop", brief="stoploop", description="Had enough? Stop looping the same song and give your ears some well-deserved peace.")
    @commands.check(is_in_same_vc)
    async def stoploop(self, ctx):
        try:
            self.loop_track = False
            await ctx.message.add_reaction('⛔')
            await ctx.send("Loop mode is OFF!")
        except Exception as e:
            print(e)
            await ctx.send("You cannot stop the loop if there is no loop, darling.")

    @commands.command(name="queue", brief="queue", description="Displays the current song queue")
    @commands.check(is_in_same_vc)
    async def queue(self, ctx):
        queue_block = await self.queue_block_str()
        #Buttons
        await ctx.send(queue_block, 
                       components=[[
                           Button(style=ButtonStyle.blue, label="First", custom_id="queue1"),
                           Button(style=ButtonStyle.blue, label="Back", custom_id="queue2"),
                           Button(style=ButtonStyle.blue, label="Next", custom_id="queue3"),
                           Button(style=ButtonStyle.blue, label="Last", custom_id="queue4")
                       ]])
    
    async def queue_block_str(self):
        queue_block = "```\n"
        starting_index = (self.queue_page-1) * 10
        for index, song_info in enumerate(self.queue[starting_index:]):
            if index > 9 or (starting_index + index) > len(self.queue):
                break
            audio_name = song_info['name'] + "-" + song_info['artist']
            audio_duration = song_info['duration']
            minutes = int(audio_duration // 60)
            seconds = audio_duration % 60
            if (index + starting_index) == self.queue_index:
                supposed_endtime = self.current_track_start_time + self.track_duration
                time_left_in_sec = supposed_endtime - time.time()
                mins = int(time_left_in_sec // 60)
                sec = round(time_left_in_sec) % 60
                if sec < 10: 
                    sec = "0" + str(sec)
                queue_block += "[Current song] ⤵\n"
                queue_block += f"{starting_index+index+1}) {audio_name}  {mins}min {sec}s left\n"
                queue_block += "[Current song] ⤴\n"
            else:
                if seconds < 10: 
                    seconds = "0" + str(seconds)
                queue_block += f"{starting_index+index+1}) {audio_name}  {minutes}:{seconds}\n"

        if len(self.queue) == 0:
            queue_block += "You have no songs in the queue now, go add some!\n```"
        else:
            total_pages = int(-(len(self.queue) // -10)) #Negation trick to imitate math.ceil
            if self.queue_page == total_pages:
                queue_block += "\nThis is the end of the queue.\n```"
            else: 
                queue_block += f"Page {self.queue_page} / {total_pages}\n```"
        return queue_block
        
    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        total_pages = int(-(len(self.queue) // -10))
        if interaction.component.custom_id == "queue1": #First button
            self.queue_page = 1
        elif interaction.component.custom_id == "queue2": #Back button
            if self.queue_page != 1:
                self.queue_page -= 1
        elif interaction.component.custom_id == "queue3": #Next button
            if self.queue_page != total_pages:
                self.queue_page += 1
        elif interaction.component.custom_id == "queue4": #Last button
            self.queue_page = total_pages
        
        if interaction.component.custom_id in ["queue1", "queue2", "queue3", "queue4"]:
            queue_block = await self.queue_block_str()
            await interaction.message.edit(queue_block, components=[[
                                              Button(style=ButtonStyle.blue, label="First", custom_id="queue1"),
                                              Button(style=ButtonStyle.blue, label="Back", custom_id="queue2"),
                                              Button(style=ButtonStyle.blue, label="Next", custom_id="queue3"),
                                              Button(style=ButtonStyle.blue, label="Last", custom_id="queue4")
                                           ]])
        await interaction.respond(type=InteractionType.UpdateMessage)

    @commands.command(name="restart", brief="restart", description="Starts playing from the beginning of the queue.")
    @commands.check(is_in_same_vc)
    async def restart(self, ctx):
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if len(self.queue) == 0:
            await ctx.send("Hey you don't even have a single song in the queue, mate.")
            return
        bot_voice_client.pause()   
        self.queue_index = -1
        self.loop_track = False
        self.queue_stopped = False
        await self.play_next(ctx)
    
    @commands.command(name="clear", brief="clear", description="Clears the current song queue.")
    @commands.check(is_in_same_vc)
    async def clear(self, ctx):
        self.queue.clear()
        self.queue_index = 0
        await ctx.send("Queue cleared!")
        
    @commands.command(name="jump", brief="jump <number>", description="Skips to the specified track in the queue.")
    @commands.check(is_in_same_vc)
    async def jump(self, ctx, pos: int):
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if len(self.queue) == 0:
            await ctx.send("Hey you don't even have a single song in the queue, mate.")
            return
        elif pos < 1 or pos > len(self.queue):
            await ctx.send("Hey give me a valid position number in the queue, don't try to break me.")
            return
        bot_voice_client.pause()
        self.queue_index = pos - 2
        self.loop_track = False
        self.queue_stopped = False
        await self.play_next(ctx)
        
    @commands.command(name="skip", brief="skip", description="Skips to the next song.")
    @commands.check(is_in_same_vc)
    async def skip(self, ctx):
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        msg = ctx.message
        if bot_voice_client.is_playing():
            self.loop_track = False
            bot_voice_client.stop()
            await ctx.send(":next_track: ***Skipped***")
        else:
            await ctx.send("LOL there's no audio playing now, what are you doing man?")
        
    @commands.command(name="back", brief="back", description="Skips to the previous song.")
    @commands.check(is_in_same_vc)
    async def back(self, ctx):
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if len(self.queue) == 0:
            await ctx.send("Hey you don't even have a single song in the queue, mate.")
            return
        if self.queue_index == 0:
            self.queue_index = len(self.queue) - 2
        bot_voice_client.pause()
        self.queue_index -= 2
        self.loop_track = False
        self.queue_stopped = False
        await self.play_next(ctx)
        await ctx.send(":previous_track: ***Back to previous song***")
        
    @commands.command(name="remove", brief="remove <number>", description="Remove the specified track in the queue.")
    @commands.check(is_in_same_vc)
    async def remove(self, ctx, pos: int):
        if len(self.queue) == 0:
            await ctx.send("Hey you don't even have a single song in the queue, mate.")
            return
        elif pos < 1 or pos > len(self.queue):
            await ctx.send("Hey give me a valid position number in the queue, don't try to break me.")
            return
        if (pos - 1) == self.queue_index: #remove the current song
            deleted_song = self.queue.pop(pos-1)
            self.loop_track = False
            bot_voice_client.stop()
        else:
            deleted_song = self.queue.pop(pos-1)
        await ctx.send(f"Deleted {deleted_song['name']} from position {pos}")
        
    @commands.command(name="shuffle", brief="shuffle", description="Shuffles the queue.")
    @commands.check(is_in_same_vc)
    async def shuffle(self, ctx):
        bot_voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if bot_voice_client is not None and bot_voice_client.is_playing():
            current_song = self.queue.pop(self.queue_index)
        random.shuffle(self.queue)
        if bot_voice_client is not None and bot_voice_client.is_playing():
            self.queue.insert(self.queue_index, current_song)
        await ctx.send("Queue shuffled!")
    
    @shuffle.error
    async def shuffle_error(self, ctx, error):
        print(error)
    
    @commands.command(name="move", brief="move <song position in queue> <new position>", description="Moves the specified song to a specific position in the queue.")
    @commands.check(is_in_same_vc)
    async def move(self, ctx, original_pos: int, new_pos: int):
        if original_pos < 1 or original_pos > len(self.queue) or new_pos < 1 or new_pos > len(self.queue):
            await ctx.send("Hey give me two valid position numbers in the queue, don't try to break me.")
        if original_pos-1 == self.queue_index:
            self.queue_index = new_pos - 1
        moved_song = self.queue.pop(original_pos-1)
        self.queue.insert(new_pos-1, moved_song)
        await ctx.send(f"Song \"{moved_song['name']}\" moved from position {original_pos} to position {new_pos}")
    
    @commands.command(name="loopqueue", brief="loopqueue", description="Loops the queue. I will play the first song again once the last song is finished playing")
    @commands.check(is_in_same_vc)
    async def loopqueue(self, ctx):
        self.loop_queue = True
        await ctx.message.add_reaction('😻')
        await ctx.send("Looping the queue!(meaning: I will start playing from the top of the queue again after the last song is finished.)\nUse the `-mtb stop` command to stop the loop!")        
    
    @commands.command(name="leave", brief="leave", description="I don't want to leave, but I have to, doesn't I?\nNever gonna run around and desert you~")
    @commands.check(is_in_same_vc)
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

    @commands.command(name="timeleft", brief="timeleft", description="Displays the time left for the current queue.")
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
            await member.guild.system_channel.send("Queue cleared!")
        
    
    @commands.Cog.listener()
    async def on_ready(self):
        my_cog = self.bot.get_cog("Music")
        Music.description = "Play some music in your voice chat. It's time to rock n roll!\n`{} total commands`".format(len(my_cog.get_commands()))
        print("Music bot ready to rock n roll!")

def setup(bot):
    bot.add_cog(Music(bot))
