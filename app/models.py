from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Playlist(db.Model):
    __tablename__ = 'playlists'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.String(100), nullable=False)
    name        = db.Column(db.String(200), nullable=False)
    spotify_id  = db.Column(db.String(100), nullable=False)
    url         = db.Column(db.String(500), nullable=False)
    track_count = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
