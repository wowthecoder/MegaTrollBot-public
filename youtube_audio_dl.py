import youtube_dl
import discord
import ctypes
import ctypes.util

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
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
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        if not url.startswith("https://"):
            #url = "https://youtu.be/" + ytdl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]['id'] 
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{url}", download=False))
        else:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if 'entries' in data:
            #take first item from a playlist
            #playlist is in the form of a dictionary, eg. data = {'entries': [all the song names here]}
            data = data['entries'][0]
        audio_url = data["formats"][0]["url"]
        audio_name = data['title'] + " - " + data['uploader']
        audio_duration = data['duration']
        #filename = ytdl.prepare_filename(data)
        #return filename
        return [audio_url, audio_name, audio_duration]

    @classmethod
    async def fun_video(cls, query, *, loop=None, stream=False):
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
