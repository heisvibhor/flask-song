from flask_restful import Resource, request, reqparse, marshal_with, fields
from flask_login import  login_required, current_user
from application.models import Playlist, SongPlaylist, Song, db, SongLikes
from sqlalchemy import func
from application.delete import delete_song

songFields = {
    'id' : fields.Integer,
    'creator_id': fields.Integer,
    'language' : fields.String,
    'image': fields.String,
    'title': fields.String,
    'views': fields.String,
    'genre' : fields.String,
    'description' : fields.String,
}
class songPlaylistResourse(Resource):
    @login_required 
    @marshal_with(songFields)
    def post(self, playlist_id, song_id):
        playlist = Playlist.query.get_or_404(playlist_id)
        song = Song.query.get_or_404(song_id)

        songplaylist = SongPlaylist.query.filter(SongPlaylist.playlist_id == playlist_id, SongPlaylist.song_id == song_id).first()
        if songplaylist or playlist.user_id != current_user.id:
            return 'Failed', 406

        playlist.songs.append(song)
        db.session.add(playlist)
        db.session.commit()

        return song, 200

    @login_required 
    def delete(self, playlist_id, song_id):
        playlist = Playlist.query.get_or_404(playlist_id)
        songplaylist = SongPlaylist.query.filter(SongPlaylist.playlist_id == playlist_id, SongPlaylist.song_id == song_id).first()
        if songplaylist and playlist.user_id == current_user.id:
            db.session.delete(songplaylist)
            db.session.commit()
            return 'Success', 202
        else:
            return 'Not Found', 401
   
songQueryFields = {
    'song' : fields.Nested(songFields),
    'rating': fields.Integer,
}

class albumSongSearchResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title')

    @marshal_with(songQueryFields)
    @login_required 
    def get(self):
        args = request.args
        query = db.select(Song, func.avg(SongLikes.rating).label('rating')).join(SongLikes , SongLikes.song_id == Song.id,isouter=True).group_by(Song.id).where(Song.creator_id == current_user.id)

        empty = ['', None, ' ']
        if args.get('title') not in empty:
            query = query.where(Song.title.ilike('%'+args['title']+'%'))
        if args.get('genre') not in empty and args.get('genre')!= 'all':
            query = query.where(Song.genre == args['genre'])
        if args.get('language') not in empty and args.get('genre')!= 'all':
            query = query.where(Song.genre == args['language'])

        res = db.session.execute(query).fetchall()
        if res[0] == (None, None):
            return 'Not found', 400
        an = [{'song': r[0], 'rating':r[1]} for r in res]
        return an
    
class songSearchResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title')
    @marshal_with(songQueryFields)
    @login_required 
    def get(self):
        args = request.args
        query = db.select(Song, func.avg(SongLikes.rating).label('rating')).join(SongLikes , SongLikes.song_id == Song.id,isouter=True).group_by(Song.id).limit(100)

        empty = ['', None, ' ']
        if args.get('title') not in empty:
            query = query.where(Song.title.ilike('%'+args['title']+'%'))
        if args.get('genre') not in empty and args.get('genre')!= 'all':
            query = query.where(Song.genre == args['genre'])
        if args.get('language') not in empty and args.get('genre')!= 'all':
            query = query.where(Song.genre == args['language'])

        res = db.session.execute(query).fetchall()
        if res[0] == (None, None):
            return 'Not found', 400
        an = [{'song': r[0], 'rating':r[1]} for r in res]
        return an
    
    @login_required
    def delete(self, song_id):
        song = Song.query.get_or_404(song_id)
        if current_user.id != song.creator_id:
            return 'Not allowed', 405

        delete_song(song_id)

        return 'Success', 202