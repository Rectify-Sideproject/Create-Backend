import base64
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
#from django_redis import get_redis_connection
import redis


load_dotenv()


def spotify_user_request(access_token:str):
    sp = spotipy.Spotify(auth=access_token)
    return sp

def spotifyconnect(scope:str):
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_SECRET_KEY')
    redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))
    return sp

class SearchSong(APIView):
    def post(self, request, format=None, *args, **kwargs):
        song_query = request.data['song_query']
        token = request.data['access_token']
        print(song_query)
        
        sp = spotify_user_request(access_token=token)
        searched_song = sp.search(q=song_query, type='track', limit=1)
        
        song_thumbnail = searched_song['tracks']['items'][0]['album']['images'][2]['url']  
        owner = searched_song['tracks']['items'][0]['album']['artists'][0]['name']
        
        duration_ms = searched_song['tracks']['items'][0]['duration_ms']
        duration_seconds = duration_ms/1000
        duration_whole_minute = int(duration_seconds / 60)
        duration_whole_second = int(duration_seconds % 60)
        duration_total = f'{duration_whole_minute}:{duration_whole_second}'
        
        result_artist_name = searched_song['tracks']['items'][0]['artists']
        
        artist = []
        for artists in range(len(result_artist_name)):
            artist.append(result_artist_name[artists]['name'])
            
        song_title = searched_song['tracks']['items'][0]['name']
        track_id = searched_song['tracks']['items'][0]['id']
        
        
        #This is a good place to start if you want to contribute to the backend
        ''' To check if searched songs are in liked songs, would like someone to fix this as there seems to be a bug
        liked_song = False
        track_id = searched_song['tracks']['items'][0]['id']
        scope = 'user-library-read'
        sp = spotifyconnect(access_token=token, scope=scope)
        saved_songs = sp.current_user_saved_tracks()
        liked_songs_many = saved_songs['items']
        liked_songs_id = []
        for songs in range(len(liked_songs_many)):
            liked_songs_id.append(liked_songs_many[songs]['track']['id'])
        
        if track_id in liked_songs_id:
            liked_song = True
        '''
        
        return Response(
            {
                'Song_details': {
                    'thumbnail': song_thumbnail,
                    'title': song_title,
                    'owner': owner,
                    'artists': artist,
                    'duration': duration_total,
                    'track_id': track_id,
                }
            },
            status=status.HTTP_201_CREATED)
    

class GetCurrentSong(APIView):
    def get(self, request, format=None, *args, **kwargs):
        scope = 'user-read-currently-playing'
        sp = spotifyconnect(scope=scope)
        currently_listening = sp.currently_playing()
        
        owner = currently_listening['item']['album']['artists'][0]['name']
        title = currently_listening['item']['name']
        
        result_artists = currently_listening['item']['artists']
        artists = []
        for artist in range(len(result_artists)):
            artists.append(result_artists[artist]['name'])
        
        thumbnail = currently_listening['item']['album']['images'][2]['url']
        
        duration_ms = currently_listening['item']['duration_ms']
        duration_seconds = duration_ms/1000
        duration_whole_minute = int(duration_seconds/60)
        duration_whole_second = int(duration_seconds%60)
        duration_total = f'{duration_whole_minute}:{duration_whole_second}'
        
        track_id = currently_listening['item']['id']
        
        return Response(
            {
                'Song_details': {
                    'thumbnail': thumbnail,
                    'title': title,
                    'owner': owner,
                    'artists': artists,
                    'duration': duration_total,
                    'track_id': track_id,
                }
            },
            status=status.HTTP_200_OK)
        

class CreatePlaylist(APIView):
    def post(self, request, format=None, *args, **kwargs):
        track_id = request.data.get('track_id')
        token = request.data['token']
        track_seed = [f'{track_id}']
        sp = spotify_user_request(token)
        recommended_songs = sp.recommendations(seed_tracks=track_seed, limit=12)
        
        playlist_list = []
        rec_song = recommended_songs['tracks']
          
        
        for tracks in range(len(recommended_songs['tracks'])):
            owner = rec_song[tracks]['album']['artists'][0]['name']
            thumbnail = rec_song[tracks]['album']['images'][2]['url']
            
            artists = []
            for artist in range(len(rec_song[tracks]['artists'])):
                artists.append(rec_song[tracks]['artists'][artist]['name'])
                
            duration_seconds = rec_song[tracks]['duration_ms'] / 1000
            duration_minutes = int(duration_seconds/60)
            duration_whole_seconds = int(duration_seconds%60)
            duration_total = f'{duration_minutes}:{duration_whole_seconds}'
            title = rec_song[tracks]['name']
            track_id = rec_song[tracks]['id']
            
            playlist_list.append({
                'track_id': track_id,
                'thumbnail': thumbnail,
                'title': title,
                'owner': owner,
                'artists': artists,
                'duration': duration_total,
            })
          
        return Response(
            {
                'playlist': playlist_list
            },
            status=status.HTTP_200_OK)
        
class CreatePlaylistOnSpotify(APIView):
    def post(self, request, format=None, *args, **kwargs):
        pass