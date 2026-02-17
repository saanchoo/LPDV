class RecommenderService:
    def __init__(self, spotify_service):
        self.sp = spotify_service

    def generate_recommendations(self, source_tracks, limit=20):
        """
        Recibe una lista de canciones 'semilla' y devuelve recomendaciones.
        Aquí es donde en el futuro podrías meter tu lógica KNN personalizada.
        """
        # 1. Validación: Spotify solo acepta 5 semillas para recomendar
        seed_tracks = source_tracks[:5]
        
        # 2. Obtener recomendaciones de la API (Algoritmo de Spotify)
        recommendations = self.sp.get_track_recommendations(seed_tracks, limit)
        
        # 3. Filtrado opcional (Ejemplo: eliminar canciones que ya estén en el historial)
        # Aquí podrías añadir lógica extra python pura.
        
        return recommendations