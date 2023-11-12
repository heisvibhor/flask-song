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


@app.route('/admin', methods=['GET'])
def get_admin_page():
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    return render_template('admin/admin.html')

@app.route('/admin/genre', methods=['GET'])
def get_genre_page():
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    genres = Genre.query.all()
    return render_template('admin/genre.html', genres = genres)

@app.route('/admin/language', methods=['GET'])
def get_lan_page():
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    
    languages = Language.query.all()
    return render_template('admin/language.html', languages = languages)

@app.route('/admin/genre', methods=['POST'])
def post_genre():
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    
    name = request.form['name'].strip()
    if name == '' or name == None:
        flash('Invalid Name')
        return redirect('/admin/genre')
    genre_get = Genre.query.filter(Genre.name.ilike(name)).first()

    if genre_get:
        flash('Invalid duplicate Name')
        return redirect('/admin/genre')
    
    gen = Genre(name = name)
    db.session.add(gen)
    db.session.commit()

    flash('Success')
    return redirect('/admin/genre')

@app.route('/admin/language', methods=['POST'])
def post_lang():
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    
    name = request.form['name'].strip()
    if name == '' or name == None:
        flash('Invalid Name')
        return redirect('/admin/language')
    genre_get = Language.query.filter(Language.name.ilike(name)).first()

    if genre_get:
        flash('Invalid duplicate Name')
        return redirect('/admin/language')
    
    gen = Language(name = name)
    db.session.add(gen)
    db.session.commit()

    flash('Success')
    return redirect('/admin/language')

