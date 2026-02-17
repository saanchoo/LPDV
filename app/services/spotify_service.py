import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

class SpotifyService:
    def __init__(self, session_token=None):
        """
        Inicializa la conexión con Spotify.
        Si tenemos un token de usuario, lo usamos. Si no, configuramos la autenticación.
        """
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
        self.scope = "user-read-recently-played playlist-modify-public"

        # Gestor de autenticación
        self.sp_oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )

        # Si ya tenemos token (el usuario está logueado), creamos el cliente
        if session_token:
            self.sp = spotipy.Spotify(auth=session_token)
        else:
            self.sp = None

    def get_auth_url(self):
        """Genera el link para que el usuario se loguee en Spotify"""
        return self.sp_oauth.get_authorize_url()

    def get_token(self, code):
        """Intercambia el código que nos da Spotify por un token real"""
        token_info = self.sp_oauth.get_access_token(code)
        return token_info

    # --- AQUÍ EMPIEZA TU LÓGICA ORIGINAL ADAPTADA ---

    def get_last_played_tracks(self, limit=20):
        """Obtiene las últimas canciones escuchadas (Tu antigua función get_last_played_tracks)"""
        results = self.sp.current_user_recently_played(limit=limit)
        tracks = []
        for item in results['items']:
            track = item['track']
            tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'uri': track['uri']
            })
        return tracks

    def get_track_recommendations(self, seed_tracks, limit=20):
        """Obtiene recomendaciones basadas en canciones semilla (Tu antigua get_track_recommendations)"""
        # Extraemos solo los IDs de las canciones semilla
        seed_ids = [track['id'] for track in seed_tracks]
        
        # Spotify permite máximo 5 semillas
        if len(seed_ids) > 5:
            seed_ids = seed_ids[:5]

        results = self.sp.recommendations(seed_tracks=seed_ids, limit=limit)
        
        recommended = []
        for track in results['tracks']:
            recommended.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'uri': track['uri']
            })
        return recommended

    def create_playlist(self, name, track_uris):
        """Crea la playlist y añade canciones (Tus antiguas create_playlist y populate_playlist juntas)"""
        user_id = self.sp.current_user()['id']
        
        # 1. Crear la playlist vacía
        playlist = self.sp.user_playlist_create(user=user_id, name=name, public=True)
        
        # 2. Añadir las canciones
        if track_uris:
            self.sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
            
        return playlist['external_urls']['spotify']