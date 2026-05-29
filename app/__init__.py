import os
from flask import Flask
from dotenv import load_dotenv
from app.models import db

load_dotenv()

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
frontend_dist = os.path.join(basedir, 'frontend', 'dist')

app = Flask(__name__, static_folder=frontend_dist, static_url_path='')

app.secret_key = os.getenv('SECRET_KEY', 'una_clave_super_secreta_por_defecto')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "lpdv.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from app.api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from app import routes

with app.app_context():
    db.create_all()