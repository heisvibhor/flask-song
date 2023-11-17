from flask_restful import Resource, request, reqparse, marshal_with, fields
from flask_login import  login_required
from application.models import *
from sqlalchemy import func

artistFields = {
    'id' : fields.Integer,
    'artist' : fields.String,
    'image': fields.String,
    'policy_violate': fields.String,
    'disabled': fields.Boolean
}

userFields = {
    'id' : fields.Integer,
    'username' : fields.String,
    'name': fields.String,
    'email': fields.String,
}
   
artistQueryFields = {
    'artist' : fields.Nested(artistFields),
    'user': fields.Nested(userFields),
    'rating': fields.Integer,
    'views': fields.Integer,
}

class artistSearchResource(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('name')

    @marshal_with(artistQueryFields)
    @login_required 
    def get(self):
        args = request.args
        query = db.select(Creator, User, func.avg(SongLikes.rating).label('rating'), func.sum(Song.views).label('views')).join(User, User.id==Creator.id).join(Song, Song.creator_id == Creator.id).join(SongLikes, Song.id == SongLikes.song_id).group_by(Creator.id).limit(50)
        empty = ['', None, ' ']
        if args.get('name') not in empty:
            query = query.where(Creator.artist.ilike('%'+args['name']+'%'))

        res = db.session.execute(query).fetchall()
        if len(res) == 0:
            return 'Not found', 400
        an = [{'artist': r[0], 'user':r[1] ,'rating':r[2], 'views':r[3]} for r in res]
        return an
    @login_required
    def delete(self, artist_id):
        args = request.args
        artist = Creator.query.get_or_404(artist_id)

        artist.disabled = True
        artist.policy_violate = args['policy']

        db.session.add(artist)
        db.session.commit()

        return 'Success', 200