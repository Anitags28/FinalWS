from sparql_manager import SPARQLManager
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieAgent:
    def __init__(self):
        self.sparql_manager = SPARQLManager()

    def get_recommendations(self, user_id):
        """
        Genera recomendaciones de películas basadas en las preferencias del usuario.
        """
        try:
            # Obtener preferencias del usuario
            preferences = self.sparql_manager.get_user_preferences(user_id)
            favorite_directors = self._get_favorite_directors(user_id)
            
            if not preferences and not favorite_directors:
                logger.info(f"No se encontraron preferencias para el usuario {user_id}")
                # Si no hay preferencias, devolver las películas mejor calificadas que no son favoritas
                return self._get_top_rated_non_favorite_movies(user_id)
            
            # Extraer y ponderar géneros preferidos
            genres = []
            if preferences:
                for pref in preferences:
                    genre = pref['genre']['value']
                    count = int(pref['count']['value'])
                    genres.extend([genre] * count)
                
                genre_counts = Counter(genres)
                top_genres = [genre for genre, _ in genre_counts.most_common(3)]
            else:
                top_genres = []
            
            # Extraer directores favoritos
            top_directors = []
            if favorite_directors:
                director_counts = Counter(favorite_directors)
                top_directors = [director for director, _ in director_counts.most_common(2)]
            
            # Obtener películas similares basadas en géneros y directores preferidos
            recommendations = self.sparql_manager.get_similar_movies(
                user_id=user_id,
                genres=top_genres,
                directors=top_directors,
                min_rating=3.5
            )
            
            # Si no hay suficientes recomendaciones, complementar con películas mejor calificadas
            if len(recommendations) < 5:
                top_rated = self._get_top_rated_non_favorite_movies(user_id, limit=5-len(recommendations))
                # Evitar duplicados
                existing_ids = {r['movie']['value'] for r in recommendations}
                for movie in top_rated:
                    if movie['movie']['value'] not in existing_ids:
                        recommendations.append(movie)
            
            return self._format_recommendations(recommendations)
        except Exception as e:
            logger.error(f"Error al generar recomendaciones: {str(e)}")
            return []

    def _get_top_rated_non_favorite_movies(self, user_id, limit=5):
        """
        Obtiene las películas mejor calificadas que no son favoritas del usuario.
        """
        try:
            all_movies = self.sparql_manager.get_all_movies()
            # Filtrar películas que ya son favoritas
            non_favorite_movies = []
            for movie in all_movies:
                movie_id = movie['movie']['value'].split('#')[1].replace('movie_', '')
                if not self.sparql_manager.is_favorite_movie(user_id, movie_id):
                    non_favorite_movies.append(movie)
            
            # Ordenar por calificación
            sorted_movies = sorted(
                non_favorite_movies,
                key=lambda x: float(x['rating']['value']),
                reverse=True
            )
            return sorted_movies[:limit]
        except Exception as e:
            logger.error(f"Error al obtener películas mejor calificadas no favoritas: {str(e)}")
            return []

    def generate_opinion(self, movie_id):
        """
        Genera una opinión sobre una película basada en sus características.
        """
        try:
            details = self.sparql_manager.get_movie_details(movie_id)
            if not details:
                return "No tengo suficiente información sobre esta película."

            rating = float(details['rating']['value'])
            genre = details['genre']['value']
            
            opinion = f"Esta es una película de {genre}. "
            
            if rating >= 4.5:
                opinion += "Es una película excepcional que no te puedes perder. "
            elif rating >= 4.0:
                opinion += "Es una muy buena película que vale la pena ver. "
            elif rating >= 3.5:
                opinion += "Es una película entretenida que puede gustarte. "
            elif rating >= 3.0:
                opinion += "Es una película decente, aunque tiene sus altibajos. "
            else:
                opinion += "Puede que esta película no sea para todos los gustos. "

            if genre == "Action":
                opinion += "Espera encontrar secuencias emocionantes y mucha adrenalina."
            elif genre == "Drama":
                opinion += "Prepárate para una historia emotiva y personajes profundos."
            elif genre == "Comedy":
                opinion += "Te hará reír y pasar un buen rato."
            elif genre == "Horror":
                opinion += "Te mantendrá al borde de tu asiento con sus momentos de tensión."
            elif genre == "Sci-Fi":
                opinion += "Te llevará a un mundo de imaginación y posibilidades."
            elif genre == "Romance":
                opinion += "Te envolverá en una historia de amor y emociones."

            return opinion
        except Exception as e:
            logger.error(f"Error al generar opinión: {str(e)}")
            return "Lo siento, no puedo generar una opinión en este momento."

    def _get_favorite_directors(self, user_id):
        """
        Obtiene los directores de las películas favoritas del usuario
        """
        try:
            query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ex: <http://example.org/movies#>
            
            SELECT ?director (COUNT(?movie) as ?count)
            WHERE {{
                ex:user_{user_id} ex:hasFavorite ?movie .
                ?movie ex:director ?director .
            }}
            GROUP BY ?director
            ORDER BY DESC(?count)
            """
            self.sparql_manager.sparql.setQuery(query)
            results = self.sparql_manager.sparql.query().convert()
            
            directors = []
            for result in results["results"]["bindings"]:
                director = result.get('director', {}).get('value')
                count = int(result.get('count', {}).get('value', 0))
                directors.extend([director] * count)
            
            return directors
        except Exception as e:
            logger.error(f"Error al obtener directores favoritos: {str(e)}")
            return []

    def _format_recommendations(self, recommendations):
        """
        Formatea las recomendaciones para su presentación y agrega explicaciones personalizadas
        """
        try:
            formatted = []
            for movie in recommendations:
                movie_id = movie['movie']['value'].split('#')[1]
                formatted.append({
                    'movie': {'value': movie['movie']['value']},
                    'title': {'value': movie['title']['value']},
                    'genre': {'value': movie['genre']['value']},
                    'director': {'value': movie['director']['value']},
                    'rating': {'value': movie['rating']['value']},
                })
            return formatted
        except Exception as e:
            logger.error(f"Error al formatear recomendaciones: {str(e)}")
            return [] 