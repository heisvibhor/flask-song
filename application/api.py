from flask_restful import Api
from flask_restful import current_app as app
from .api_resources.creator import creatorResourse, creatorPolicyResourse
from .api_resources.song import songPlaylistResourse, albumSongSearchResource, songSearchResource

api = Api(app)
api.add_resource(creatorResourse, '/api/creator',)
api.add_resource(creatorPolicyResourse, '/api/creator', '/api/creator/<int:creator_id>')
api.add_resource(songPlaylistResourse, '/api/playlist/<int:playlist_id>/<int:song_id>')
api.add_resource(albumSongSearchResource, '/api/album/song/search')
api.add_resource(songSearchResource, '/api/song/search')
