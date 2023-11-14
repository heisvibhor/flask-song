from flask_login import login_required, current_user
from flask import request, current_app as app, redirect, render_template
from .models import *
from sqlalchemy import case, func


@app.route('/', methods = ['GET'])
@login_required
def index():
    name = current_user.username

    data = {}

    if current_user.user_type == 'ADMIN':
        return render_template('admin/admin.html')
    
    base_query = db.select(Song).order_by(case(
        (Song.language == current_user.language, 1),
        else_ = 0
    )).limit(10)
    query = base_query.join(SongLikes , SongLikes.song_id == Song.id,isouter=True).group_by(Song.id).order_by(func.avg(SongLikes.rating))
    data['top_rated'] = db.session.execute(query).all()

    query1 = base_query.order_by(Song.views)
    data['top_views'] = db.session.execute(query1).all()

    query2 = base_query.order_by(Song.created_at.desc()).order_by(Song.views)
    data['recently_added'] = db.session.execute(query2).all()

    query3 = db.select(Playlist).order_by(Playlist.created_at.desc()).filter(Playlist.is_album==True).limit(10)
    data['albums'] = db.session.execute(query3).all()

    query4 = db.select(Playlist).order_by(Playlist.created_at.desc()).filter(Playlist.is_album==False, Playlist.user_id == current_user.id)
    data['playlists'] = db.session.execute(query4).all()

    user = {
        'name' : current_user.name,
        'id' : current_user.id,
        'email' : current_user.email,
        'image' : current_user.image
    }

    print(data)
    return render_template('user/index.html', user = user, data = data)