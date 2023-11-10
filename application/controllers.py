from flask_login import login_required, current_user
from flask import request, current_app as app, redirect, send_file, render_template, flash
from .models import *
import os

@app.route('/', methods = ['GET'])
@login_required
def index():
    name = current_user.username

    if current_user.user_type == 'ADMIN':
        return render_template('admin.html')
    return render_template('user/index.html', name = name)


@app.route('/creator', methods = ['GET'])
@login_required
def creator():
    if current_user.user_type == 'USER':
        return render_template('creator/register_creator.html')
    else:
        return render_template('creator/creator.html')
    
@app.route('/creator/song/add', methods = ['GET'])
@login_required
def add_song():
    return render_template('creator/song/add_song.html')

@app.route('/policy', methods = ['GET'])
def policy():
    return render_template('policy.html')

@app.route('/creator/song/edit/<int:song_id>', methods = ['GET'])
@login_required
def post_song(song_id):
    get_song = Song.query.get_or_404(song_id)
    return render_template('creator/song/update_song.html', song = get_song)

@app.route("/song/<string:filename>")
def return_audio(filename):
    name = app.config['AUDIO_FOLDER'] +"\\" +filename
    if os.path.exists(name):
        return send_file(name)
    else:
        return None, 404

@app.route("/image/<string:filename>")
def return_image(filename):
    name = app.config['IMAGE_FOLDER'] +"\\" +filename
    if os.path.exists(name):
        return send_file(name)
    else:
        return None, 404

@app.route("/listen/<int:song_id>")
def listen(song_id):
    song_get = Song.query.get_or_404(song_id)
    def template(song):
        return render_template('user/song_thumb.html', song = song)
    return render_template('user/listen.html', song = song_get, give = template)
