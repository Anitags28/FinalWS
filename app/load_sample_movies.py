from sparql_manager import SPARQLManager
import time

sample_movies = [
    {"title": "Inception", "director": "Christopher Nolan", "genre": "Sci-Fi", "rating": 4.8},
    {"title": "Titanic", "director": "James Cameron", "genre": "Romance", "rating": 4.7},
    {"title": "The Dark Knight", "director": "Christopher Nolan", "genre": "Action", "rating": 4.9},
    {"title": "Forrest Gump", "director": "Robert Zemeckis", "genre": "Drama", "rating": 4.6},
    {"title": "The Matrix", "director": "Lana Wachowski, Lilly Wachowski", "genre": "Sci-Fi", "rating": 4.8},
    {"title": "Pulp Fiction", "director": "Quentin Tarantino", "genre": "Crime", "rating": 4.7},
    {"title": "La La Land", "director": "Damien Chazelle", "genre": "Musical", "rating": 4.3},
    {"title": "El laberinto del fauno", "director": "Guillermo del Toro", "genre": "Fantasy", "rating": 4.5},
    {"title": "Avengers: Endgame", "director": "Anthony Russo, Joe Russo", "genre": "Action", "rating": 4.4},
    {"title": "Coco", "director": "Lee Unkrich, Adrian Molina", "genre": "Animation", "rating": 4.6},
    {"title": "Parasite", "director": "Bong Joon-ho", "genre": "Thriller", "rating": 4.7},
    {"title": "Amélie", "director": "Jean-Pierre Jeunet", "genre": "Romance", "rating": 4.4},
    {"title": "Gladiator", "director": "Ridley Scott", "genre": "Action", "rating": 4.5},
    {"title": "Toy Story", "director": "John Lasseter", "genre": "Animation", "rating": 4.3},
    {"title": "El secreto de sus ojos", "director": "Juan José Campanella", "genre": "Crime", "rating": 4.6},
]

def main():
    manager = SPARQLManager()
    for movie in sample_movies:
        # Generar un ID único basado en timestamp y título
        movie_id = str(int(time.time() * 1000)) + movie["title"].replace(" ", "").lower()
        movie_data = movie.copy()
        movie_data["id"] = movie_id
        try:
            manager.add_movie(movie_data)
            print(f'Película agregada: {movie["title"]}')
        except Exception as e:
            print(f'Error al agregar {movie["title"]}: {e}')
        time.sleep(0.1)  # Pequeña pausa para evitar IDs duplicados

if __name__ == "__main__":
    main() 