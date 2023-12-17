from flask_login import login_required, current_user
from flask import request, current_app as app, redirect, render_template, flash
from .models import *
import uuid
import os
from sqlalchemy import func, distinct, or_

def errorPage(message, id):
    flash('Error ' + message)
    return redirect('/creator/album/' + str(id))

def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)   
        print('File Deleted')
    else:
        print('File Not found')

def redirectCreator(user):
    if user.user_type != 'CREATOR':
        return True
    creator = Creator.query.get_or_404(user.id)
    if creator.disabled:
        return True
    return False

def statistics(creator_id):
    stats = {}
    song_count = Song.query.where(Song.creator_id == creator_id).count()
    album_count = Playlist.query.where(Playlist.user_id == creator_id, Playlist.is_album==True).count()
    query = db.select(func.sum(Song.views).label('views'), func.avg(SongLikes.rating).label('rating')).join(SongLikes , SongLikes.song_id == Song.id,isouter=True).where(Song.creator_id == creator_id)
    res = db.session.execute(query).first()
    
    query = db.select(func.count(SongLikes.like).label('likes')).join(Song , SongLikes.song_id == Song.id).where(Song.creator_id == creator_id, SongLikes.like == True)
    res1 = db.session.execute(query).first()

    query = db.select(func.count(Playlist.id)).join(SongPlaylist).where(Playlist.user_id == creator_id, Playlist.is_album == True)
    res2 = db.session.execute(query).first()

    query = db.select(func.count(distinct(Playlist.id))).join(SongPlaylist).join(Song).where(Song.creator_id == creator_id, Playlist.is_album == False)
    res3 = db.session.execute(query).first()

    stats['song_count'] = song_count
    stats['album_count'] = album_count
    stats['total_views'] = res[0] if res else 0
    stats['total_likes'] = res1[0] if res1 else 0
    stats['average_rating'] = res[1] if res else 0
    stats['songs_in_album'] = res2[0] if res2 else 0
    stats['playlist_with_songs'] = res3[0] if res3 else 0
    #No of playlist having some songs
    return stats

@app.route('/creator/song/add', methods = ['GET'])
@login_required
def add_song():
    if current_user.user_type != 'CREATOR':
        return redirect('/')
    creator = Creator.query.get_or_404(current_user.id)
    if creator.disabled:
        return redirect('/creator/policy')
    genres = Genre.query.all()
    languages = Language.query.all()
    return render_template('creator/song/add_song.html', genres = genres, languages= languages)

@app.route('/creator/song/edit/<int:song_id>', methods = ['GET'])
@login_required
def post_song(song_id):
    if current_user.user_type != 'CREATOR':
        return redirect('/')
    creator = Creator.query.get_or_404(current_user.id)
    if creator.disabled:
        return redirect('/creator/policy')
    get_song = Song.query.get_or_404(song_id)
    genres = Genre.query.all()
    languages = Language.query.all()
    return render_template('creator/song/update_song.html', song = get_song, genres = genres, languages= languages)
    
@app.route('/creator/policy')
@login_required
def policy_violated():
    if current_user.user_type == 'USER':
        return redirect('/creator')
    creator = Creator.query.get_or_404(current_user.id)
    if creator.disabled:
        return render_template('creator/policy_violate.html', creator =creator )
    return redirect('/')

@app.route('/creator', methods = ['GET'])
@login_required
def creator():
    if current_user.user_type == 'USER':
        return render_template('creator/register_creator.html')

    creator = Creator.query.get_or_404(current_user.id)
    if creator.disabled:
        return redirect('/creator/policy')
    albums = Playlist.query.filter(Playlist.user_id == current_user.id, Playlist.is_album==True).order_by(Playlist.created_at.desc()).all()
    creator.songs = Song.query.filter(Song.creator_id == current_user.id).order_by(Song.created_at.desc()).all()
    return render_template('creator/creator.html', creator = creator, albums = albums, statistics = statistics(current_user.id))

@app.route("/creator/add", methods=['POST'])
@login_required 
def post_creator_add():
    if current_user.user_type != 'CREATOR':
        return redirect('/')
    creator = Creator.query.get_or_404(current_user.id)
    if creator.disabled:
        return redirect('/creator/policy')

    artist_name = request.form['artist']
    image = request.files['image']
    if image.filename=='':
        image_filename = None
    else:
        image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
    if image_filename:
        image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))

    get_user = User.query.get_or_404(current_user.id)
    get_creator = Creator.query.filter(or_(Creator.artist == artist_name, Creator.id == current_user.id)).first()

    if get_creator:
        return errorPage(400, 'Invalid artist name or user')

    get_user.user_type = 'CREATOR'
    new_creator = Creator(id = current_user.id, artist = artist_name, image = image_filename)
    db.session.add(new_creator, get_user)
    db.session.commit()
    return redirect('/creator')


@app.route('/creator/update')
@login_required
def update_creator_get():
    if current_user.user_type != 'CREATOR':
        return redirect('/')
    creator = Creator.query.get_or_404(current_user.id)
    if creator.disabled:
        return redirect('/creator/policy')
    
    return render_template('creator/edit_register.html', creator = creator)

@app.route('/creator/update' ,methods = ['POST'])
@login_required
def update_creator_post():
    if current_user.user_type != 'CREATOR':
        return redirect('/')
    creator = Creator.query.get_or_404(current_user.id)
    if creator.disabled:
        return redirect('/creator/policy')

    artist = request.form.get('artist')
    image = request.files['image']

    empty = [None, '', ' ']

    if image.filename=='':
        image_filename =  None
    else:
        if creator.image:
            delete_file(os.path.join(app.config['IMAGE_FOLDER'] , creator.image))
        
        image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
        creator.image = image_filename

        if image_filename:
            image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))

    if artist in empty:
        flash('Invalid Inputs')
        return redirect('/profile')
    
    if artist != creator.artist:
        user_get = Creator.query.where(Creator.artist == artist).first()
        if user_get:
            flash('Creator already exists login!')
            return redirect('/profile')

    db.session.add(creator)
    db.session.commit()
        
    return redirect('/creator')

@app.route('/creator/album/<string:album_id>', methods = ['GET'])
@login_required
def creator_album(album_id):
    if current_user.user_type != 'CREATOR':
        return redirect('/')
    creator = Creator.query.get_or_404(current_user.id)
    if creator.disabled:
        return redirect('/creator/policy')

    if album_id =='new':
        genres = Genre.query.all()
        return render_template('creator/album/new_album.html', genres = genres)
    else:
        play = Playlist.query.get_or_404(int(album_id))
        genres = Genre.query.all()
        return render_template('creator/album/update_album.html', album = play, genres = genres)
    
@app.route('/creator/album/song/<int:album_id>', methods = ['GET'])
@login_required
def album_song(album_id):
    if current_user.user_type != 'CREATOR':
        return redirect('/')
    creator = Creator.query.get_or_404(current_user.id)
    if creator.disabled:
        return redirect('/creator/policy')
    play = Playlist.query.get_or_404(album_id)
    genres = Genre.query.all()
    languages = Language.query.all()
    return render_template('creator/album/song.html', album = play, genres = genres, languages= languages)
    
@app.route('/creator/album/new', methods = ['POST'])
@login_required
def creator_album_post():
    if current_user.user_type != 'CREATOR':
        return redirect('/')
    creator = Creator.query.get_or_404(current_user.id)
    if creator.disabled:
        return redirect('/creator/policy')
    image = request.files['image']

    if image.filename=='':
        image_filename = None
    else:
        image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
    
    empty = ['', None, ' ']

    playlist = Playlist(user_id = current_user.id, is_album = True) 

    if request.form['title'] not in empty :
        playlist.title = request.form['title'] 
    else :
        return errorPage('Invalid Album Title', 'new')
    
    playlist.description = request.form['description'] if request.form['description'] not in empty else None

    if image_filename:
        playlist.image = image_filename
        image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))
                                
    db.session.add(playlist)
    db.session.commit()

    return redirect('/creator/album/song/' + str(playlist.id))


@app.route('/creator/album/edit/<int:album_id>', methods = ['POST'])
@login_required
def creator_album_put(album_id):
    if current_user.user_type != 'CREATOR':
        return redirect('/')
    creator = Creator.query.get_or_404(current_user.id)
    if creator.disabled:
        return redirect('/creator/policy')
    image = request.files['image']

    playlist = Playlist.query.get_or_404(int(album_id))
    empty = ['', None, ' ']
    if request.form['title'] not in empty :
        playlist.title = request.form['title'] 
    else :
        return errorPage('Invalid Album Title', album_id)

    if image.filename=='':
        image_filename =  None
    else:
        if playlist.image:
            delete_file(os.path.join(app.config['IMAGE_FOLDER'] , playlist.image))
        
        image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
        playlist.image = image_filename
    
    playlist.description = request.form['description'] if request.form['description'] not in empty else None

    if image_filename:
        print('file')
        image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))
                                
    db.session.add(playlist)
    db.session.commit()

    return redirect('/creator/album/song/' + str(playlist.id))


