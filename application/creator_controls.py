from flask_login import login_required, current_user
from flask import request, current_app as app, redirect, send_file, render_template, flash
from .models import *
import uuid
import os

def errorPage(message, id):
    flash('Error ' + message)
    return redirect('/creator/album/' + str(id))

def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)   
        print('File Deleted')
    else:
        print('File Not found')

@app.route('/creator', methods = ['GET'])
@login_required
def creator():
    if current_user.user_type == 'USER':
        return render_template('creator/register_creator.html')
    else:
        return render_template('creator/creator.html')


@app.route('/creator/album/<string:album_id>', methods = ['GET'])
@login_required
def creator_album(album_id):
    if current_user.user_type == 'USER':
        return redirect('/')
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
    if current_user.user_type == 'USER':
        return redirect('/')
    play = Playlist.query.get_or_404(album_id)
    genres = Genre.query.all()
    languages = Language.query.all()
    return render_template('creator/album/song.html', album = play, genres = genres, languages= languages)
    
@app.route('/creator/album/new', methods = ['POST'])
@login_required
def creator_album_post():
    if current_user.user_type == 'USER':
        return redirect('/')
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
    if current_user.user_type == 'USER':
        return redirect('/')
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

def statistics(creator_id):
    # count albums
    # count playlists
    # total likes
    # total views 
    # total ratings
    # count of songs used in playlist

    song_count = Song.query.where(Song.creator_id == creator_id).count()
    song_usage_count = db.session.query(SongPlaylist).first()
    
    # query =db.select([Song.id])
    # song_ids = db.execute(query).fetchall()
    song_ids = Song.query.with_entities(Song.id).filter(Song.creator_id == creator_id).all()

    arr = [i for (i,) in song_ids]

    new = db.session.query(SongPlaylist).filter(SongPlaylist.song_id.in_(arr)).all()
    print(song_usage_count.song.creator_id, song_count, song_ids, new, arr)
    
# print(statistics(1))