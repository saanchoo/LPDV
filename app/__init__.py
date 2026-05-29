import os
from flask import Flask
from dotenv import load_dotenv
from app.models import db

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'una_clave_super_secreta_por_defecto')

# SQLite — el archivo lpdv.db se crea junto a run.py
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "lpdv.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from app import routes
from app.api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

with app.app_context():
    db.create_all()