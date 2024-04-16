from django.urls import path
from .views import *

urlpatterns = [
    path('search/', SearchSong.as_view(), name='spotify_search'),
    path('getcurrentsong/', GetCurrentSong.as_view(), name='getcurrentsong'),
    path('createplaylist/', CreatePlaylist.as_view(), name='createplaylist'),
]
