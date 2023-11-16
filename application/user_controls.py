from flask_login import login_required, current_user
from flask import request, current_app as app, redirect, render_template
from .models import *
from sqlalchemy import case, func
import json


@app.route('/songthumb/<int:song_id>')
def thumb(song_id):
    song = Song.query.get_or_404(song_id)
    res = {}
    return render_template('user/song_thumb.html', song = song)
    res['script'] = render_template('user/song_thumb_script.js', song = song)
    return json.dumps(res)

@app.route('/script.js')
def script():
    return render_template('user/song_thumb_script.js')

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
    data['top_rated'] = [song for song, in db.session.execute(query).all()]

    query1 = base_query.order_by(Song.views)
    data['top_views'] = [song for song, in db.session.execute(query1).all()]

    query2 = base_query.order_by(Song.created_at.desc()).order_by(Song.views)
    data['recently_added'] = [song for song, in db.session.execute(query2).all()]

    query3 = db.select(Playlist, Creator).order_by(Playlist.created_at.desc()).join(Creator, Creator.id == Playlist.user_id).filter(Playlist.is_album==True).limit(10)
    data['albums'] = db.session.execute(query3).all()

    query4 = db.select(Playlist).order_by(Playlist.created_at.desc()).filter(Playlist.is_album==False, Playlist.user_id == current_user.id)
    data['playlists'] = [playlist for playlist, in db.session.execute(query4).all()]

    user = {
        'name' : current_user.name,
        'id' : current_user.id,
        'email' : current_user.email,
        'image' : current_user.image
    }

    print(data)

    return render_template('user/index.html', user = user, data = data)