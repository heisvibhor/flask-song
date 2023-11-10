from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.orm import Mapped, relationship

from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)
    user_type = db.Column(db.String, db.CheckConstraint('user_type in ("USER", "CREATOR", "ADMIN")'), default = "USER")
    playlists = db.relationship('Playlist', backref = 'user')

class Creator(db.Model):
    __tablename__ = 'creator'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    artist = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, server_default=db.sql.func.now())
    disabled = db.Column(db.Boolean, default = False)
    policy_violate = db.Column(db.String)
    songs = db.relationship('Song', backref = 'creator')

class Song(db.Model):
    __tablename__ = 'song'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable = False)
    description = db.Column(db.String, nullable = False)
    creator_id = db.Column(db.Integer, db.ForeignKey("creator.id"), nullable=False)
    lyrics = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.sql.func.now())
    audio = db.Column(db.String)
    image = db.Column(db.String)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    playlists : Mapped[list["SongPlaylist"]] = relationship( back_populates='song', cascade="save-update")

class Playlist(db.Model):
    __tablename__ = 'playlist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable = False)
    is_album = db.Column(db.Boolean, default = False)
    description = db.Column(db.String, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.sql.func.now())
    image = db.Column(db.String)
    songs: Mapped[list["SongPlaylist"]]  = relationship( back_populates='playlist')

class SongPlaylist(db.Model):
    __tablename__ = "song_playlist"
    song_id = db.Column(db.Integer, db.ForeignKey("song.id"), primary_key=True, nullable=False)
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlist.id"), primary_key=True, nullable=False)
    song : Mapped["Song"]  = relationship( back_populates='playlists')
    playlist : Mapped["Playlist"]  = relationship( back_populates='songs')
    order = db.Column(db.Integer, nullable=False)
