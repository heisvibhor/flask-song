from flask_login import login_required, current_user
from flask import request, current_app as app, redirect, send_file, render_template, flash
from .models import *
from flask_restful import marshal_with, fields
import json
import os



    
@app.route('/creator/song/add', methods = ['GET'])
@login_required
def add_song():
    genres = Genre.query.all()
    languages = Language.query.all()
    return render_template('creator/song/add_song.html', genres = genres, languages= languages)

@app.route('/policy', methods = ['GET'])
def policy():
    return render_template('policy.html')

@app.route('/creator/song/edit/<int:song_id>', methods = ['GET'])
@login_required
def post_song(song_id):
    get_song = Song.query.get_or_404(song_id)
    genres = Genre.query.all()
    languages = Language.query.all()
    return render_template('creator/song/update_song.html', song = get_song, genres = genres, languages= languages)

@app.route("/song/<string:filename>")
@login_required
def return_audio(filename):
    name = app.config['AUDIO_FOLDER'] +"\\" +filename
    if os.path.exists(name):
        return send_file(name)
    else:
        return None, 404

@app.route("/image/<string:filename>")
@login_required
def return_image(filename):
    name = app.config['IMAGE_FOLDER'] +"\\" +filename
    if os.path.exists(name):
        return send_file(name)
    else:
        return send_file(app.config['IMAGE_FOLDER'] +"\\default.jpg")

@app.route("/listen/<int:song_id>", methods=['GET'])
@login_required
def listen(song_id):
    song_get = Song.query.get_or_404(song_id)
    def template(song):
        return render_template('user/song_thumb.html', song = song)
    return render_template('user/listen.html', song = song_get, give = template)


@app.route("/rating/<int:song_id>/<int:rate>", methods=['PUT'])
@login_required
def rating(song_id, rate):
    if not(rate<= 5 and rate>=0):
        return None, 405
    get = SongLikes.query.filter(SongLikes.song_id == song_id, SongLikes.user_id == current_user.id).first()

    if get:
        get.rating = rate
        db.session.add(get)
        db.session.commit()
        return json.dumps("Success"), 200
        
    new = SongLikes(song_id = song_id, user_id = current_user.id, rating=rate)
    db.session.add(new)
    db.session.commit()
    return json.dumps("Success"), 200

field = {
    'rating': fields.Integer,
    'like': fields.Boolean,
}

@app.route("/rating/<int:song_id>")
@login_required
@marshal_with(field)
def get_rating(song_id):
    get = SongLikes.query.filter(SongLikes.song_id == song_id, SongLikes.user_id == current_user.id).first()

    if get:
        return get, 200
        
    new = SongLikes(song_id = song_id, user_id = current_user.id)
    db.session.add(new)
    db.session.commit()
    return new, 200

@app.route("/like/<int:song_id>", methods=['PUT'])
@login_required
def like(song_id):
    get = SongLikes.query.filter(SongLikes.song_id == song_id, SongLikes.user_id == current_user.id).first()

    if get:
        get.like = True
        db.session.add(get)
        db.session.commit()
        return json.dumps("Success"), 200
        
    new = SongLikes(song_id = song_id, user_id = current_user.id, like = True)
    db.session.add(new)
    db.session.commit()
    return json.dumps("Success"), 200

@app.route("/unlike/<int:song_id>", methods=['PUT'])
@login_required
def unlike(song_id):
    get = SongLikes.query.filter(SongLikes.song_id == song_id, SongLikes.user_id == current_user.id).first()

    if get:
        get.like = False
        db.session.add(get)
        db.session.commit()
        return json.dumps("Success"), 200
        
    new = SongLikes(song_id = song_id, user_id = current_user.id, like = False)
    db.session.add(new)
    db.session.commit()
    return json.dumps("Success"), 200
