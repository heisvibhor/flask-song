from flask_login import login_required, current_user
from flask import request, current_app as app, redirect, render_template, flash
from .models import *
import uuid
import os

def errorPage(message, id):
    flash('Error ' + message)
    return redirect('/playlist/edit/' + str(id))

def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)   
        print('File Deleted')
    else:
        print('File Not found')

@app.route('/playlist/edit/<string:playlist_id>', methods = ['GET'])
@login_required
def playlist_init(playlist_id):
    if playlist_id =='new':
        genres = Genre.query.all()
        return render_template('user/playlist/new.html', genres = genres)
    else:
        play = Playlist.query.get_or_404(int(playlist_id))
        if play.is_album:
            return redirect('/')
        genres = Genre.query.all()
        return render_template('user/playlist/update.html', playlist = play, genres = genres)
    
@app.route('/playlist/<int:playlist_id>', methods = ['GET'])
@login_required
def playlist_view(playlist_id):
    play = Playlist.query.get_or_404(playlist_id)
    if current_user.id != play.user_id:
        return redirect('/')
    if play.is_album:
        return redirect('/')
    genres = Genre.query.all()
    languages = Language.query.all()
    return render_template('user/playlist/page.html', playlist = play, genres = genres, languages= languages)

@app.route('/album/<int:album_id>', methods = ['GET'])
@login_required
def album_view(album_id):
    album = Playlist.query.get_or_404(album_id)
    if not album.is_album:
        return redirect('/')
    return render_template('user/album.html', album = album)
    
@app.route('/playlist/new', methods = ['POST'])
@login_required
def playlist_create():
    image = request.files['image']

    if image.filename=='':
        image_filename = None
    else:
        image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
    
    empty = ['', None, ' ']

    playlist = Playlist(user_id = current_user.id, is_album = False) 

    if request.form['title'] not in empty :
        playlist.title = request.form['title'] 
    else :
        return errorPage('Invalid Playlist Title', 'new')
    
    playlist.description = request.form['description'] if request.form['description'] not in empty else None

    if image_filename:
        playlist.image = image_filename
        image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))
                                
    db.session.add(playlist)
    db.session.commit()

    return redirect('/playlist/' + str(playlist.id))


@app.route('/playlist/edit/<int:playlist_id>', methods = ['POST'])
@login_required
def playlist_edit(playlist_id):
    
    image = request.files['image']

    playlist = Playlist.query.get_or_404(int(playlist_id))
    if current_user.id != playlist.user_id:
        return redirect('/')
    if playlist.is_album:
        return redirect('/')
    empty = ['', None, ' ']
    if request.form['title'] not in empty :
        playlist.title = request.form['title'] 
    else :
        return errorPage('Invalid Playlist Title', playlist_id)

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

    return redirect('/playlist/' + str(playlist.id))


