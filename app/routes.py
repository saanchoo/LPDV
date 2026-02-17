from flask import render_template, request, redirect, session, url_for
from app import app
from app.services.spotify_service import SpotifyService

@app.route('/')
def index():
    if 'token_info' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html', logged_in=False)


@app.route('/login')
def login():
    # Creamos servicio solo para obtener la URL de login
    service = SpotifyService()
    auth_url = service.get_auth_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Spotify nos devuelve a esta URL con un código
    code = request.args.get('code')
    service = SpotifyService()
    token_info = service.get_token(code)
    
    # Guardamos el token en la "memoria" del navegador (sesión)
    session['token_info'] = token_info
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    # Protegemos la ruta: si no hay token, al login
    if 'token_info' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/crear_playlist', methods=['POST'])
def crear_playlist():
    # Recuperamos el token de la sesión
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('login'))

    # Inicializamos el servicio con el token del usuario
    sp = SpotifyService(session_token=token_info['access_token'])

    # 1. Obtener datos del formulario
    num_tracks = int(request.form.get('num_tracks', 10))
    playlist_name = request.form.get('playlist_name', 'Playlist del Vago')

    # 2. Tu lógica: Obtener historial
    last_played = sp.get_last_played_tracks(limit=num_tracks)

    # 3. Tu lógica: Usar esas canciones para recomendaciones
    # (Usamos las 5 primeras como "semilla" automáticamente para simplificar al vago)
    seed_tracks = last_played[:5]
    recommendations = sp.get_track_recommendations(seed_tracks=seed_tracks, limit=20)

    # 4. Tu lógica: Crear playlist y llenarla
    track_uris = [track['uri'] for track in recommendations]
    playlist_url = sp.create_playlist(name=playlist_name, track_uris=track_uris)

    return f"<h1>¡Playlist Creada!</h1><a href='{playlist_url}'>Abrir en Spotify</a>"