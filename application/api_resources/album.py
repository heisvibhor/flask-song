from flask_restful import Resource, Api, request, reqparse, marshal_with, fields
from flask_login import  login_required, current_user
from werkzeug.exceptions import HTTPException
from flask import make_response, redirect, url_for, flash
from flask_restful import current_app as app
from application.models import *
from application.delete import delete_playlist

artistFields = {
    'id' : fields.Integer,
    'artist' : fields.String,
    'image': fields.String,
    'policy_violate': fields.String,
    'disabled' : fields.Boolean
}

albumFields = {
    'id' : fields.Integer,
    'title' : fields.String,
    'image': fields.String,
    'description': fields.String,
    'created_at' : fields.DateTime,
}
   
albumQueryFields = {
    'artist' : fields.Nested(artistFields),
    'album': fields.Nested(albumFields),
}

class albumSearchResource(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('name')

    @marshal_with(albumQueryFields)
    @login_required 
    def get(self):
        args = request.args
        query = db.select(Creator, Playlist).join(Creator, Playlist.user_id == Creator.id).where(Playlist.is_album == True).limit(50)
        empty = ['', None, ' ']
        if args.get('title') not in empty:
            query = query.where(Playlist.title.ilike('%'+args['title']+'%'))

        res = db.session.execute(query).fetchall()
        if len(res) == 0:
            return 'Not found', 400
        an = [{'artist': r[0], 'album':r[1] } for r in res]
        return an
    @login_required
    def delete(self, album_id):
        album = Playlist.query.get_or_404(album_id)
        if current_user.id != album.user_id and current_user.user_type != 'ADMIN':
            return 'Not allowed', 405

        delete_playlist(album_id)

        return 'Success', 202