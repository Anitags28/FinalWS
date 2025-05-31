from flask import Flask, render_template, request, jsonify
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
from sparql_manager import SPARQLManager
from movie_agent import MovieAgent
import os
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)

# Configuración de namespaces
EX = Namespace("http://example.org/movies#")
movie_agent = MovieAgent()
sparql_manager = SPARQLManager()

@app.route('/')
def index():
    try:
        # Obtener todas las películas para mostrar en la interfaz
        movies = sparql_manager.get_all_movies()
        return render_template('index.html', movies=movies)
    except Exception as e:
        logger.error(f"Error en la página principal: {str(e)}")
        return render_template('index.html', movies=[], error="Error al cargar las películas")

@app.route('/add_movie', methods=['POST'])
def add_movie():
    try:
        data = request.json
        if not all(key in data for key in ['title', 'director', 'genre', 'rating']):
            return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400
        
        # Asignar un ID único basado en timestamp
        data['id'] = str(int(time.time() * 1000))
        
        # Validar datos
        if not isinstance(data['rating'], (int, float)) or not (1 <= data['rating'] <= 5):
            return jsonify({"status": "error", "message": "La calificación debe ser un número entre 1 y 5"}), 400
        
        if not data['title'].strip():
            return jsonify({"status": "error", "message": "El título no puede estar vacío"}), 400
        
        if not data['director'].strip():
            return jsonify({"status": "error", "message": "El director no puede estar vacío"}), 400
        
        # Agregar la película
        sparql_manager.add_movie(data)
        
        return jsonify({
            "status": "success",
            "message": "Película agregada correctamente",
            "movie": {
                "id": data['id'],
                "title": data['title'],
                "director": data['director'],
                "genre": data['genre'],
                "rating": data['rating']
            }
        })
    except Exception as e:
        logger.error(f"Error al agregar película: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_recommendations')
def get_recommendations():
    try:
        user_id = request.args.get('user_id', '1')  # Usuario por defecto
        recommendations = movie_agent.get_recommendations(user_id)
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error al obtener recomendaciones: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/movie_details/<movie_id>')
def movie_details(movie_id):
    try:
        details = sparql_manager.get_movie_details(movie_id)
        if not details:
            return jsonify({"status": "error", "message": "Película no encontrada"}), 404
        
        opinion = movie_agent.generate_opinion(movie_id)
        return jsonify({
            "status": "success",
            "details": details,
            "opinion": opinion
        })
    except Exception as e:
        logger.error(f"Error al obtener detalles de película: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/is_favorite/<movie_id>')
def is_favorite(movie_id):
    try:
        user_id = request.args.get('user_id', '1')
        is_favorite = sparql_manager.is_favorite_movie(user_id, movie_id)
        return jsonify({
            "status": "success",
            "is_favorite": is_favorite
        })
    except Exception as e:
        logger.error(f"Error al verificar favorito: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/favorite_movie', methods=['POST'])
def add_favorite_movie():
    try:
        data = request.json
        if not all(key in data for key in ['user_id', 'movie_id']):
            return jsonify({"status": "error", "message": "Faltan datos requeridos"}), 400
        
        # Verificar si ya es favorita
        is_favorite = sparql_manager.is_favorite_movie(data['user_id'], data['movie_id'])
        
        if is_favorite:
            # Si ya es favorita, la quitamos de favoritos
            sparql_manager.remove_favorite_movie(data['user_id'], data['movie_id'])
            message = "Película eliminada de favoritos"
        else:
            # Si no es favorita, la agregamos a favoritos
            sparql_manager.add_favorite_movie(data['user_id'], data['movie_id'])
            message = "Película agregada a favoritos"
        
        return jsonify({
            "status": "success",
            "message": message
        })
    except Exception as e:
        logger.error(f"Error al modificar favorito: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_all_movies')
def get_all_movies():
    try:
        movies = sparql_manager.get_all_movies()
        return jsonify({
            "status": "success",
            "movies": movies
        })
    except Exception as e:
        logger.error(f"Error al obtener todas las películas: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    logger.info(f"Templates directory: {TEMPLATE_DIR}")
    app.run(debug=True) 