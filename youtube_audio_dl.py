import youtube_dl
import discord
import ctypes
import ctypes.util
from copy import deepcopy

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'playliststart': 1,
    'playlistend': 1,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default-search': 'auto',
    'source_address': '0.0.0.0'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ytdl._ies = [ytdl.get_info_extractor('Youtube'),
             ytdl.get_info_extractor('YoutubeWatchLater'),
             ytdl.get_info_extractor('YoutubeYtUser'),
             ytdl.get_info_extractor('YoutubeFavourites'),
             ytdl.get_info_extractor('YoutubeHistory'),
             ytdl.get_info_extractor('YoutubeTab'),
             ytdl.get_info_extractor('YoutubePlaylist'),
             ytdl.get_info_extractor('YoutubeRecommended'),
             ytdl.get_info_extractor('YoutubeSearchDate'),
             ytdl.get_info_extractor('YoutubeSearch'),
             ytdl.get_info_extractor('YoutubeSubscriptions'),
             ytdl.get_info_extractor('YoutubeTruncatedID'),
             ytdl.get_info_extractor('YoutubeTruncatedURL'),
             ytdl.get_info_extractor('YoutubeYtBe')]

class YTDLSource(discord.PCMVolumeTransformer):
    #The init method is useless as of now because it is only called when an instance of the class is created
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        if not url.startswith("https://"):
            #url = "https://youtu.be/" + ytdl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]['id'] 
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{url}", download=False))
        else:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        audio_url = data["formats"][0]["url"]
        audio_ytid = data["id"]
        audio_duration = data['duration']
        #filename = ytdl.prepare_filename(data)
        #return filename
        return [audio_url, data['title'], data['uploader'], audio_ytid, audio_duration]
        
    @classmethod
    async def song_from_playlist(cls, url, index, loop=None):
        playlist_format_options = deepcopy(ytdl_format_options)
        playlist_format_options["playliststart"] = index
        playlist_format_options["playlistend"] = index
        custom_ytdl = youtube_dl.YoutubeDL(playlist_format_options)
        data = custom_ytdl.extract_info(url, download=False)
        if len(data["entries"]) == 0:
            return False
        else:
            song = data["entries"][0]
            audio_url = song["formats"][0]["url"]
            audio_name = song["title"]
            audio_artist = song["uploader"]
            audio_ytid = song["id"]
            audio_duration = song["duration"]
            return [audio_url, audio_name, audio_artist, audio_ytid, audio_duration]
    
    @classmethod
    async def fun_video(cls, query, *, loop=None):
        video_info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        video_id = video_info['id']
        video_name = video_info['title']
        video_description = video_info['description']
        if len(video_description) > 200: 
            video_description = video_description[:200]
            last_space_index = video_description.rfind(" ")
            video_description = video_description[:last_space_index]
            video_description += "..."
        return [video_id, video_name, video_description]
