from flask_restful import Resource, Api, request, reqparse, marshal_with, fields
from flask_login import  login_required, current_user
from werkzeug.exceptions import HTTPException
from flask import make_response, redirect, url_for, flash
from flask_restful import current_app as app
from application.models import Playlist, SongPlaylist, Song, db
from sqlalchemy import or_


class songPlaylistResourse(Resource):
    @login_required 
    def post(self, playlist_id, song_id):
        playlist = Playlist.query.get_or_404(playlist_id)
        song = Song.query.get_or_404(song_id)

        songplaylist = SongPlaylist.query.filter(SongPlaylist.playlist_id == playlist_id, SongPlaylist.song_id == song_id).first()
        if songplaylist:
            return 'Failed', 402

        playlist.songs.append(song)
        db.session.add(playlist)
        db.session.commit()

        return 'Success', 200

    @login_required 
    def delete(self, playlist_id, song_id):
        songplaylist = SongPlaylist.query.filter(SongPlaylist.playlist_id == playlist_id, SongPlaylist.song_id == song_id).first()
        if songplaylist:
            db.session.delete(songplaylist)
            db.session.commit()
            return 'Success', 202
        else:
            return 'Not Found', 401
        
songFields = {
    'id' : fields.Integer,
    'creator_id': fields.Integer,
    'image': fields.String,
    'title': fields.String,
}

class albumSongSearchResource(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('title')

    @marshal_with(songFields)
    @login_required 
    def get(self):
        args = request.args
        print('Now')
        query = db.session.query(Song).where(Song.creator_id == current_user.id)

        empty = ['', None, ' ']
        if args.get('title') not in empty:
            query = query.where(Song.title.ilike('%'+args['title']+'%'))
        if args.get('genre') not in empty and args.get('genre')!= 'all':
            query = query.where(Song.genre == args['genre'])
        if args.get('language') not in empty and args.get('genre')!= 'all':
            query = query.where(Song.genre == args['language'])

        return query.all()