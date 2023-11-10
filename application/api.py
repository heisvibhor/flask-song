from flask_restful import Api
from flask_restful import current_app as app
from .api_resources.creator import creatorResourse, creatorPolicyResourse

api = Api(app)
api.add_resource(creatorResourse, '/api/creator',)
api.add_resource(creatorPolicyResourse, '/api/creator', '/api/creator/<int:creator_id>')