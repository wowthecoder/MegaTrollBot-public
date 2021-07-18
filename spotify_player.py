import discord
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import youtube_audio_dl
import ctypes
import ctypes.util

client_id = "Your client ID here"
client_secret = "Your client secret here"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

class SpotifyDL(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self,data = data
        self.title = data.get('title')
        self.url= ""
        
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        track_info = spotify.track(url)
        track_artist = track_info['artists'][0]['name']
        track_name = track_info['name']
        track_query = track_artist + " " + track_name
        audio_info = await youtube_audio_dl.YTDLSource.from_url(track_query, loop=loop)
        return [audio_info[0], track_artist + " - " + track_name, audio_info[2]]

    @classmethod
    async def songs_from_playlist(cls, url, index, loop=None, stream=False):
        playlist = spotify.playlist_items(url)
        track = playlist['items'][index]['track']
        track_artist = track['artists'][0]['name']
        track_name = track['name']
        track_query = track_artist + " " + track_name
        audio_info = await youtube_audio_dl.YTDLSource.from_url(track_query, loop=loop)
        return audio_info
            
    @classmethod
    async def num_of_songs(cls, url):
        playlist = spotify.playlist_items(url)
        return len(playlist['items'])
            
        
        
