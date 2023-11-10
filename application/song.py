from flask_login import  login_required, current_user
from werkzeug.exceptions import HTTPException
from flask import make_response, redirect, flash, request, current_app as app
from application.models import Song, db
import json
import os
import uuid

class MessageError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {'error_code': error_code,'error_message': error_message}
        self.response = make_response(json.dumps(message), status_code)

def errorPage(code, message):
    flash('Error ' + str(code) + ' ' + message)
    return redirect('/creator/song/add')

def putPageError(code, message, song_id):
    flash('Error ' + str(code) + ' ' + message)
    return redirect('/creator/song/edit/'+song_id)

def homeRedirect():
    return redirect('/')

def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)   
        print('File Deleted')
    else:
        print('File Not found')
    
@login_required
def delete(song_id):
    if current_user.user_type != 'CREATOR':
        return homeRedirect()
    get_song = Song.query.get_or_404(song_id)
    if current_user.id != get_song.id:
        return errorPage(400, 'Invalid User to perform the action')
    # todo delete img and mp3 file
    db.session.delete(get_song)
    db.session.commit()

@app.route('/song/update/<int:song_id>', methods = ['post'])
@login_required
def put(song_id):
    if current_user.user_type != 'CREATOR':
        return homeRedirect()

    get_song = Song.query.get_or_404(song_id)

    audio = request.files['audio']
    image = request.files['image']

    if audio.filename=='':
        audio_filename = None
    else:
        if get_song.audio:
            delete_file(os.path.join(app.config['AUDIO_FOLDER'] , get_song.audio))
        
        audio_filename = 'a' + str(uuid.uuid4()) +'.' + audio.filename.split('.')[-1]
        get_song.audio = audio_filename

    if image.filename=='':
        image_filename =  None
    else:
        if get_song.image:
            delete_file(os.path.join(app.config['IMAGE_FOLDER'] , get_song.image))
        
        image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
        get_song.image = image_filename
    
    empty = ['', None, ' ']

    if request.form['title'] not in empty :
        get_song.title = request.form['title'] 
    else :
        return putPageError(400, 'Invalid Song Title', get_song.id)
    
    get_song.lyrics = request.form['lyrics'] if request.form['lyrics'] not in empty else None
    get_song.description = request.form['description'] if request.form['description'] not in empty else None
    
    if not (get_song.audio or get_song.lyrics):
        return putPageError(400, 'Both audio and lyrics cannot be empty', get_song.id)

    if audio_filename:
        audio.save(os.path.join(app.config['AUDIO_FOLDER'] , audio_filename))
    if image_filename:
        image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))

    db.session.add(get_song)
    db.session.commit()

    flash('Updated succesfully')
    return redirect('/creator/song/edit/' + str(get_song.id))

@app.route('/song/add', methods = ['post'])
@login_required 
def post():
    if current_user.user_type != 'CREATOR':
        return homeRedirect()

    audio = request.files['audio']
    image = request.files['image']

    if audio.filename=='':
        audio_filename = None
    else:
        audio_filename = 'a' + str(uuid.uuid4()) +'.' + audio.filename.split('.')[-1]
    if image.filename=='':
        image_filename = None
    else:
        image_filename = 'a' + str(uuid.uuid4()) +'.' + image.filename.split('.')[-1]
    
    empty = ['', None, ' ']

    new_song = Song(audio = audio_filename, image = image_filename)
    if request.form['title'] not in empty :
        new_song.title = request.form['title'] 
    else :
        return errorPage(400, 'Invalid Song Title')
    
    new_song.creator_id = current_user.id
    new_song.lyrics = request.form['lyrics'] if request.form['lyrics'] not in empty else None
    new_song.description = request.form['description'] if request.form['description'] not in empty else None
    
    if not (new_song.audio or new_song.lyrics):
        return errorPage(400, 'Both audio and lyrics cannot be empty')

    if audio_filename:
        audio.save(os.path.join(app.config['AUDIO_FOLDER'] , audio_filename))
    if image_filename:
        image.save(os.path.join(app.config['IMAGE_FOLDER'] , image_filename))

    db.session.add(new_song)
    db.session.commit()

    return redirect('/creator')