from flask import Flask
from application.models import db
import os

app = Flask(__name__)
with app.app_context():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///proj.sqlite3'
    app.config['SECRET_KEY'] = 'hullahullagullarasgulla'
    app.config['IMAGE_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "image")
    app.config['AUDIO_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "audio")
    db.init_app(app)
app.app_context().push()



from application.login import *
from application.controllers import *
from application.api import *
from application.song import *
from application.creator_controls import *
from application.admin_controls import *
from application.user_controls import *
from application.playlist import *

if __name__ == '__main__':
    app.run(host='::', port ="5001", debug=True, threaded = False)