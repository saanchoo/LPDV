import os
from flask import send_from_directory
from app import app


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    dist = app.static_folder
    target = os.path.join(dist, path)
    if path and os.path.isfile(target):
        return send_from_directory(dist, path)
    return send_from_directory(dist, 'index.html')
