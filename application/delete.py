import os
from .models import db, Song, Playlist
from flask import current_app as app

def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)   
        print('File Deleted')
    else:
        print('File Not found')

def delete_song(song_id):
    get_song = Song.query.get_or_404(song_id)

    get_song.playlists = []
    get_song.likes = []
    
    if get_song.image:
        delete_file(os.path.join(app.config['IMAGE_FOLDER'] , get_song.image))
    if get_song.audio:
        delete_file(os.path.join(app.config['AUDIO_FOLDER'] , get_song.audio))

    db.session.delete(get_song)
    db.session.commit()


def delete_playlist(playlist_id):
    get_playlist = Playlist.query.get_or_404(playlist_id)
    
    get_playlist.songs = []
    if get_playlist.image:
        delete_file(os.path.join(app.config['IMAGE_FOLDER'] , get_playlist.image))

    db.session.delete(get_playlist)
    db.session.commit()