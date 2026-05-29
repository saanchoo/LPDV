import os
from flask import Blueprint, jsonify, session, request, redirect
from app.services.spotify_service import SpotifyService
from app.models import db, Playlist
from spotipy.oauth2 import SpotifyOAuth

api_bp = Blueprint('api', __name__)

FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')


def _get_oauth():
    return SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope="user-read-recently-played playlist-modify-public"
    )


def get_spotify():
    """Devuelve un SpotifyService autenticado, renovando el token si está caducado."""
    token_info = session.get('token_info')
    if not token_info:
        return None
    sp_oauth = _get_oauth()
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info
    return SpotifyService(session_token=token_info['access_token'])


# ─── AUTH ────────────────────────────────────────────────────────────────────

@api_bp.route('/auth/login')
def api_login():
    service = SpotifyService()
    return redirect(service.get_auth_url())


@api_bp.route('/auth/callback')
def api_callback():
    code = request.args.get('code')
    service = SpotifyService()
    token_info = service.get_token(code)
    session['token_info'] = token_info
    return redirect(f'{FRONTEND_URL}/?auth=success')


@api_bp.route('/auth/status')
def api_auth_status():
    sp = get_spotify()
    if not sp:
        return jsonify({'logged_in': False, 'user': None})
    user = sp.sp.current_user()
    return jsonify({
        'logged_in': True,
        'user': {
            'id': user['id'],
            'name': user['display_name'],
            'image': user['images'][0]['url'] if user.get('images') else None
        }
    })


@api_bp.route('/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})


# ─── TRACKS ──────────────────────────────────────────────────────────────────

@api_bp.route('/tracks/recent')
def api_recent_tracks():
    sp = get_spotify()
    if not sp:
        return jsonify({'error': 'No autenticado'}), 401
    raw = sp.get_last_played_tracks(limit=50)
    # Deduplicar por ID manteniendo orden
    seen, unique = set(), []
    for t in raw:
        if t['id'] not in seen:
            seen.add(t['id'])
            unique.append(t)
    return jsonify({'tracks': unique[:20]})


@api_bp.route('/tracks/search')
def api_search_tracks():
    sp = get_spotify()
    if not sp:
        return jsonify({'error': 'No autenticado'}), 401
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'tracks': []})
    tracks = sp.search_tracks(q)
    return jsonify({'tracks': tracks})


# ─── PLAYLIST ────────────────────────────────────────────────────────────────

@api_bp.route('/playlist/generate', methods=['POST'])
def api_generate():
    sp = get_spotify()
    if not sp:
        return jsonify({'error': 'No autenticado'}), 401

    data = request.get_json() or {}
    seed_tracks = data.get('seed_tracks', [])   # seleccionadas por el usuario
    num_songs = int(data.get('num_songs', 20))  # tamaño deseado de la playlist

    if not seed_tracks:
        return jsonify({'error': 'Selecciona al menos una canción semilla'}), 400

    recommendations = sp.get_track_recommendations(seed_tracks=seed_tracks, limit=num_songs)

    return jsonify({'seed_tracks': seed_tracks, 'recommendations': recommendations})


@api_bp.route('/playlist/create', methods=['POST'])
def api_create():
    # ── Diagnóstico: muestra en consola los scopes reales del token ──
    token_info = session.get('token_info', {})
    token_scope = token_info.get('scope', 'SIN SCOPE INFO')
    print(f"\n[LPDV] Scopes del token: {token_scope}")
    print(f"[LPDV] ¿tiene playlist-modify-public? {'playlist-modify-public' in token_scope}")
    print(f"[LPDV] ¿tiene playlist-modify-private? {'playlist-modify-private' in token_scope}\n")

    sp = get_spotify()
    if not sp:
        return jsonify({'error': 'No autenticado'}), 401

    data = request.get_json() or {}
    name = data.get('name', 'Playlist del Vago')
    track_uris = data.get('track_uris', [])

    try:
        playlist_url = sp.create_playlist(name=name, track_uris=track_uris)
    except Exception as e:
        error_str = str(e)
        if '403' in error_str:
            return jsonify({
                'error': 'Spotify no permite crear playlists desde esta app. '
                         'Ve al Spotify Developer Dashboard → tu app → Settings → '
                         'User Management y añade tu cuenta de Spotify como usuario permitido.'
            }), 403
        return jsonify({'error': f'Error de Spotify: {error_str}'}), 500

    playlist_id = playlist_url.split('/')[-1]

    user = sp.sp.current_user()
    record = Playlist(
        user_id=user['id'],
        name=name,
        spotify_id=playlist_id,
        url=playlist_url,
        track_count=len(track_uris)
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({'success': True, 'playlist_url': playlist_url, 'playlist_id': playlist_id})


# ─── HISTORY ─────────────────────────────────────────────────────────────────

@api_bp.route('/history')
def api_history():
    sp = get_spotify()
    if not sp:
        return jsonify({'playlists': []})

    user = sp.sp.current_user()
    records = (Playlist.query
               .filter_by(user_id=user['id'])
               .order_by(Playlist.created_at.desc())
               .all())

    return jsonify({'playlists': [
        {
            'id': r.id,
            'name': r.name,
            'url': r.url,
            'track_count': r.track_count,
            'created_at': r.created_at.isoformat()
        }
        for r in records
    ]})
