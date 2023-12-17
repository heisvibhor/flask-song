from flask_login import login_required, current_user
from flask import request, current_app as app, redirect, render_template, flash
from .models import *
from sqlalchemy import case, func
from werkzeug.security import generate_password_hash
from .delete import delete_file
import uuid
import os


@app.route('/songthumb/<int:song_id>')
@login_required
def thumb(song_id):
    song = Song.query.get_or_404(song_id)
    return render_template('user/song_thumb.html', song = song)

@app.route('/script.js')
@login_required
def script():
    return render_template('user/song_thumb_script.js')

@app.route('/', methods = ['GET'])
@login_required
def index():
    data = {}

    if current_user.user_type == 'ADMIN':
        return redirect('/admin')
    
    base_query = db.select(Song).order_by(case(
        (Song.language == current_user.language, 0),
        else_ = 1
    )).limit(10)
    query = base_query.join(SongLikes , SongLikes.song_id == Song.id,isouter=True).group_by(Song.id).order_by(func.avg(SongLikes.rating).desc())
    data['top_rated'] = [song for song, in db.session.execute(query).all()]

    query1 = base_query.order_by(Song.views.desc())
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

    # print(data)

    return render_template('user/index.html', user = user, data = data)

@app.route('/search/song', methods=['GET'])
@login_required
def user_song_serach():
    genres = Genre.query.all()
    languages = Language.query.all()
    return render_template('/user/search_song.html', songs = None, genres = genres, languages= languages)

@app.route('/search/song', methods=['POST'])
@login_required
def user_song_serach_page():
    title = request.form['title']
    genre = request.form['genre']
    language = request.form['language']
    query = db.select(Song, func.avg(SongLikes.rating).label('rating')).join(SongLikes, Song.id == SongLikes.song_id, isouter=True).group_by(Song.id).limit(50)
    empty = ['', None, ' ', 'undefined','all']
    if title not in empty:
        query = query.where(Song.title.ilike('%'+title+'%'))
    if genre not in empty:
        query = query.where(Song.genre.ilike('%'+genre+'%'))
    if language not in empty:
        query = query.where(Song.language.ilike('%'+language+'%'))
    print(query)
    res = db.session.execute(query).fetchall()
    if len(res) == 0:
        flash('Not Found')
        return redirect('/search/song')
    an = [{'song': r[0] ,'rating':r[1]} for r in res]
    genres = Genre.query.all()
    languages = Language.query.all()
    return render_template('/user/search_song.html', songs = an, genres = genres, languages= languages)


@app.route('/search/album', methods=['GET'])
@login_required
def user_album_serach():
    return render_template('/user/search_album.html', albums = None)

@app.route('/search/album', methods=['POST'])
@login_required
def user_album_serach_res():
    title = request.form['title']
    query = db.select(Playlist, Creator).where(Playlist.is_album == True).join(Creator, Creator.id == Playlist.user_id).limit(50)
    empty = ['', None, ' ', 'undefined']
    if title not in empty:
        query = query.where(Playlist.title.ilike('%'+title+'%'))
    res = db.session.execute(query).fetchall()
    if len(res) == 0:
        flash('Not Found')
        return redirect('/search/album')
  
    return render_template('/user/search_album.html', albums = res)

@app.route('/profile')
@login_required
def get_profile():
    languages = Language.query.all()
    return render_template('user/profile.html', user = current_user, languages= languages)

@app.route('/profile', methods=['POST'])
@login_required
def post_profile():

    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('change_password')
    name = request.form.get('name')
    language = request.form.get('language')

    image = request.files['image']

    user = User.query.get_or_404(current_user.id)
    empty = [None, '', ' ']

    if image.filename=='':
        image_filename =  None
    else:
        if user.image:
            delete_file(os.path.join(app.config['IMAGE_FOLDER'] , user.image))
        
        image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
        user.image = image_filename

        if image_filename:
            image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))

    if email in empty or username in empty or name in empty or language in empty:
        flash('Invalid Inputs')
        return redirect('/profile')
    
    if username != user.username:
        user_get = User.query.where(User.username == username).first()
        if user_get:
            flash('User already exists login!')
            return redirect('/profile')
        
    if password not in empty:
        user.password = generate_password_hash(password)

    user.username = username
    user.email = email
    user.name = name
    user.language = language

    db.session.add(user)
    db.session.commit()
        
    return redirect('/')