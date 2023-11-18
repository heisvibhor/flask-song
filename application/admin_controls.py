from flask_login import login_required, current_user
from flask import request, current_app as app, redirect, render_template, flash, url_for
from .models import *
from .delete import delete_playlist, delete_song
import os
from sqlalchemy import func, distinct
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import matplotlib 
matplotlib.use('Agg')

colors = mcolors.XKCD_COLORS

def errorPage(message, id):
    flash('Error ' + message)
    return redirect('/creator/album/' + str(id))

def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)   
        print('File Deleted')
    else:
        print('File Not found')

def get_plot(df):
    df['Color'] = np.random.choice(list(mcolors.XKCD_COLORS), df.shape[0])

    plt.bar('Genre', 'Rating', color='Color', data=df) 
    plt.title('Genre wise ratings')
    plt.xlabel('Genre') 
    plt.ylabel('Rating') 
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.28)
    plt.savefig(os.path.join('.\\static','plot.jpg'))
    plt.close()

    plt.bar('Genre', 'Views', color='Color', data=df) 
    plt.title('Genre wise views')
    plt.xlabel('Genre') 
    plt.ylabel('Views') 
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.28)
    plt.savefig(os.path.join('.\\static','plot1.jpg'))
    plt.close()

    plt.bar('Genre', 'Count', color='Color', data=df) 
    plt.title('Genre wise count of songs uploaded')
    plt.xlabel('Genre') 
    plt.ylabel('Count') 
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.28)
    plt.savefig(os.path.join('.\\static','plot2.jpg'))
    plt.close()
    

def statistics():
    stats = {}
    song_count = Song.query.count()
    album_count = Playlist.query.where(Playlist.is_album==True).count()
    playlist_count = Playlist.query.where(Playlist.is_album==False).count()

    query = db.select(func.sum(Song.views).label('views'), func.avg(SongLikes.rating).label('rating')).join(SongLikes , SongLikes.song_id == Song.id,isouter=True)
    res = db.session.execute(query).first()
    
    query = db.select(func.count(SongLikes.like).label('likes')).where(SongLikes.like == True)
    res1 = db.session.execute(query).first()

    # Total Number of songs in playlist
    query = db.select(func.count(Playlist.id)).join(SongPlaylist).where(Playlist.is_album == True)
    res2 = db.session.execute(query).first()

    query = db.select(func.count(Playlist.id)).join(SongPlaylist).where(Playlist.is_album == False)
    res3 = db.session.execute(query).first()



    query = db.select(Genre.name, func.sum(Song.views).label('views'), func.avg(SongLikes.rating).label('rating'), func.count(distinct(Song.id)).label('count'), ).join(Song, Song.genre == Genre.name, isouter=True).join(SongLikes , SongLikes.song_id == Song.id,isouter=True).group_by(Genre.name)
    print(query)
    res4 = db.session.execute(query).fetchall()
    
    dic = [{'Genre': r[0], 'Views': r[1], 'Rating': r[2], 'Count': r[3]} for r in res4]
    df = pd.DataFrame(dic)
    df.fillna(0, inplace=True)
    get_plot(df)

    stats['song_count'] = song_count
    stats['album_count'] = album_count
    stats['playlist_count'] = playlist_count
    stats['total_views'] = res[0] if res else 0
    stats['total_likes'] = res1[0] if res1 else 0
    stats['average_rating'] = res[1] if res else 0
    stats['total_songs_in_albums'] = res2[0] if res2 else 0
    stats['total_songs_in_playlists'] = res3[0] if res2 else 0
    #No of playlist having some songs

    return stats
    

@app.route('/admin', methods=['GET'])
@login_required
def get_admin_page():
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    query1 = db.select(Song).order_by(Song.views).limit(10)
    songs = db.session.execute(query1).all()
    return render_template('admin/admin.html', statistics = statistics(), songs = songs)

@app.route('/admin/genre', methods=['GET'])
@login_required
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
@login_required
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
@login_required
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

@app.route('/admin/creator', methods=['GET'])
@login_required
def get_search_page():
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    return render_template('/admin/search_creator.html', artists = None)

@app.route('/admin/creator/block/<int:artist_id>', methods=['GET'])
@login_required
def get_block(artist_id):
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    artist = Creator.query.get_or_404(artist_id)
    return render_template('/admin/block.html', artist = artist)

@app.route('/admin/creator/block/<int:artist_id>', methods=['POST'])
@login_required
def post_block(artist_id):
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    artist = Creator.query.get_or_404(artist_id)
    artist.disabled = True
    artist.policy_violate = request.form['policy_violate']
    db.session.add(artist)
    db.session.commit()
    flash('Blocked Successfully')
    return redirect('/admin/creator')

@app.route('/admin/creator/unblock/<int:artist_id>', methods=['GET'])
@login_required
def post_unblock(artist_id):
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    artist = Creator.query.get_or_404(artist_id)
    artist.disabled = False
    artist.policy_violate = None
    db.session.add(artist)
    db.session.commit()
    flash('Unblocked Successfully')
    return redirect('/admin/creator')

@app.route('/admin/creator', methods=['POST'])
@login_required
def get_search_res():
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    name = request.form['name']
    query = db.select(Creator, User, func.avg(SongLikes.rating).label('rating'), func.sum(Song.views).label('views')).join(User, User.id==Creator.id).join(Song, Song.creator_id == Creator.id).join(SongLikes, Song.id == SongLikes.song_id).group_by(Creator.id).limit(50)
    empty = ['', None, ' ', 'undefined']
    if name not in empty:
        query = query.where(Creator.artist.ilike('%'+name+'%'))

    res = db.session.execute(query).fetchall()
    if len(res) == 0:
        flash('Not Found')
        return render_template('/admin/search_creator.html', artists = None)
    an = [{'artist': r[0], 'user':r[1] ,'rating':r[2], 'views':r[3]} for r in res]
    return render_template('/admin/search_creator.html', artists = an)


@app.route('/admin/song', methods=['GET'])
@login_required
def song_search_page():
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    genres = Genre.query.all()
    languages = Language.query.all()
    return render_template('/admin/delete_song.html', songs = None, genres = genres, languages= languages)

@app.route('/admin/song/delete/<int:song_id>', methods=['GET'])
@login_required
def post_song_delete(song_id):
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    delete_song(song_id)
    flash('Deleted Successfully')
    return redirect('/admin/song')

@app.route('/admin/song', methods=['POST'])
@login_required
def song_search_res():
    if current_user.user_type != 'ADMIN':
        return redirect('/')
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
        return redirect('/admin/song')
    an = [{'song': r[0] ,'rating':r[1]} for r in res]
    genres = Genre.query.all()
    languages = Language.query.all()
    return render_template('/admin/delete_song.html', songs = an, genres = genres, languages= languages)

@app.route('/admin/album', methods=['GET'])
@login_required
def album_search_page():
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    return render_template('/admin/delete_album.html', albums = None)

@app.route('/admin/album/delete/<int:alubm_id>', methods=['GET'])
@login_required
def album_dlete(alubm_id):
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    delete_playlist(alubm_id)
    flash('Deleted Successfully')
    return redirect('/admin/album')

@app.route('/admin/album', methods=['POST'])
@login_required
def album_search_res():
    if current_user.user_type != 'ADMIN':
        return redirect('/')
    title = request.form['title']
    query = db.select(Playlist).where(Playlist.is_album == True).limit(50)
    empty = ['', None, ' ', 'undefined']
    if title not in empty:
        query = query.where(Playlist.title.ilike('%'+title+'%'))
    res = db.session.execute(query).fetchall()
    if len(res) == 0:
        flash('Not Found')
        return redirect('/admin/album')
  
    return render_template('/admin/delete_album.html', albums = res)