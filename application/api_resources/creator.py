from flask_restful import Resource, Api, request
from flask_login import  login_required, current_user
from werkzeug.exceptions import HTTPException
from flask import make_response, redirect, url_for, flash
from flask_restful import current_app as app
from application.models import Creator,User, db
from sqlalchemy import or_


def errorPage(code, message):
    flash('Error ' + str(code) + ' ' + message)
    return redirect('/creator')

class creatorResourse(Resource):
    @login_required 
    def post(self):
        if current_user.user_type == 'CREATOR':
            return errorPage(400, 'Invalid User to perform the action')

        artist_name = request.form['artist']

        get_user = User.query.get_or_404(current_user.id)
        get_creator = Creator.query.filter(or_(Creator.artist == artist_name, Creator.id == current_user.id)).first()

        if get_creator:
            return errorPage(400, 'Invalid artist name or user')

        get_user.user_type = 'CREATOR'
        new_creator = Creator(id = current_user.id, artist = artist_name)
        db.session.add(new_creator, get_user)
        db.session.commit()

        return redirect('/creator')

class creatorPolicyResourse(Resource):
    @login_required
    def post(self, todo, creator_id):
        if current_user.user_type != 'ADMIN':
            raise errorPage(400, 'Invalid User to perform the action')
        get_creator = Creator.query.get_or_404(creator_id)
        
        if todo == 'ENABLE':
            get_creator.disabled = False
            get_creator.policy_violate = None
        elif todo == 'DISABLE':
            get_creator.policy_violate = request.form['policy_violate']
            get_creator.disabled = True 

        db.session.add(get_creator)
        db.session.commit()