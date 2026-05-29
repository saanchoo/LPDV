import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler
import os

class SpotifyService:
    def __init__(self, session_token=None):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
        self.scope = "user-read-private user-read-recently-played playlist-modify-public playlist-modify-private"

        # MemoryCacheHandler evita que Spotipy use el fichero .cache en disco,
        # que puede devolver un token viejo (sin playlist-modify-public) ignorando
        # el código de autorización nuevo.
        self.sp_oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            cache_handler=MemoryCacheHandler()
        )

        if session_token:
            self.access_token = session_token
            self.sp = spotipy.Spotify(auth=session_token)
        else:
            self.access_token = None
            self.sp = None

    def get_auth_url(self):
        # show_dialog=true fuerza la pantalla de consentimiento de Spotify aunque
        # el usuario ya haya aceptado antes — garantiza que se aprueben todos los
        # scopes actuales (incluyendo playlist-modify-public)
        return self.sp_oauth.get_authorize_url() + '&show_dialog=true'

    def get_token(self, code):
        # check_cache=False: fuerza el intercambio del código por un token fresco,
        # nunca devuelve un token cacheado de una sesión anterior.
        return self.sp_oauth.get_access_token(code, check_cache=False)

    def get_last_played_tracks(self, limit=20):
        results = self.sp.current_user_recently_played(limit=limit)
        tracks = []
        for item in results['items']:
            track = item['track']
            tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'artist_id': track['artists'][0]['id'],
                'uri': track['uri'],
                'image': track['album']['images'][-1]['url'] if track['album']['images'] else ''
            })
        return tracks

    def search_tracks(self, query, limit=8):
        results = self.sp.search(q=query, type='track', limit=limit, market='from_token')
        tracks = []
        for track in results['tracks']['items']:
            tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'artist_id': track['artists'][0]['id'],
                'uri': track['uri'],
                'image': track['album']['images'][-1]['url'] if track['album']['images'] else ''
            })
        return tracks

    def _track_to_dict(self, track):
        return {
            'id': track['id'],
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'artist_id': track['artists'][0]['id'],
            'uri': track['uri'],
            'image': track['album']['images'][-1]['url'] if track['album']['images'] else ''
        }

    def get_track_recommendations(self, seed_tracks, limit=20, **audio_features):
        """
        Estrategia multi-pasada. Development Mode de Spotify limita search a 20
        resultados por llamada, así que compensamos con más pasadas distintas.
        """
        seen_ids = {t['id'] for t in seed_tracks}
        recommended = []
        artists = list(dict.fromkeys(t['artist'] for t in seed_tracks))

        def _collect(query):
            nonlocal recommended
            if len(recommended) >= limit:
                return
            try:
                # market='from_token' evita enviar market=None que Spotify rechaza con 400
                results = self.sp.search(q=query, type='track', limit=10, market='from_token')
                for track in results['tracks']['items']:
                    if track['id'] not in seen_ids and len(recommended) < limit:
                        recommended.append(self._track_to_dict(track))
                        seen_ids.add(track['id'])
            except Exception:
                pass

        # Pase 1 — artista exacto (una llamada por artista)
        for artist in artists:
            _collect(f'artist:"{artist}"')

        # Pase 2 — nombre de canción semilla
        if len(recommended) < limit:
            for t in seed_tracks:
                _collect(t['name'])

        # Pase 3 — artista sin comillas (resultados más amplios)
        if len(recommended) < limit:
            for artist in artists:
                _collect(artist)

        # Pase 4 — combinación de artistas
        if len(recommended) < limit and len(artists) > 1:
            _collect(' '.join(artists[:3]))

        # Pase 5 — "artista + canción" para variedad adicional
        if len(recommended) < limit:
            for t in seed_tracks:
                _collect(f'{t["artist"]} {t["name"]}')

        # Pase 6 — buscar el álbum de cada semilla
        if len(recommended) < limit:
            for t in seed_tracks:
                if t.get('artist_id'):
                    _collect(f'artist:"{t["artist"]}" year:2020-2026')
                    _collect(f'artist:"{t["artist"]}" year:2015-2020')

        return recommended[:limit]

    def create_playlist(self, name, track_uris):
        import requests as req
        user_id = self.sp.current_user()['id']
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        # Intento 1: /me/playlists (equivalente sin user_id explícito)
        r = req.post(
            'https://api.spotify.com/v1/me/playlists',
            headers=headers,
            json={'name': name, 'public': True}
        )
        print(f"[LPDV] POST /me/playlists → {r.status_code}: {r.text[:300]}")

        if not r.ok:
            # Intento 2: /users/{id}/playlists (endpoint clásico)
            r = req.post(
                f'https://api.spotify.com/v1/users/{user_id}/playlists',
                headers=headers,
                json={'name': name, 'public': True}
            )
            print(f"[LPDV] POST /users/.../playlists → {r.status_code}: {r.text[:300]}")
            r.raise_for_status()

        playlist = r.json()
        if track_uris:
            self.sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
        return playlist['external_urls']['spotify']
