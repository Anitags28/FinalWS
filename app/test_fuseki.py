from sparql_manager import SPARQLManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_fuseki_connection():
    try:
        sparql_manager = SPARQLManager()
        
        # Intentar agregar una película de prueba
        test_movie = {
            'id': 'test001',
            'title': 'Test Movie',
            'director': 'Test Director',
            'genre': 'Action',
            'rating': 4.5
        }
        
        logger.info("Intentando agregar película de prueba...")
        sparql_manager.add_movie(test_movie)
        logger.info("Película agregada correctamente")
        
        # Intentar recuperar la película
        logger.info("Intentando recuperar detalles de la película...")
        movie_details = sparql_manager.get_movie_details('test001')
        if movie_details:
            logger.info("Película recuperada correctamente:")
            logger.info(f"Título: {movie_details['title']['value']}")
            logger.info(f"Director: {movie_details['director']['value']}")
            logger.info(f"Género: {movie_details['genre']['value']}")
            logger.info(f"Calificación: {movie_details['rating']['value']}")
        else:
            logger.error("No se pudo recuperar la película")
            
    except Exception as e:
        logger.error(f"Error al conectar con Fuseki: {str(e)}")
        raise

if __name__ == '__main__':
    test_fuseki_connection() 