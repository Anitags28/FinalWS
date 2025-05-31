from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS
import os
import requests
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class SPARQLManager:
    def __init__(self):
        self.endpoint = os.getenv('FUSEKI_ENDPOINT', 'http://localhost:3030/movies')
        self.admin_endpoint = 'http://localhost:3030'
        self.dataset_name = 'movies'
        
        # Configurar endpoints
        self.sparql = SPARQLWrapper(f"{self.endpoint}/query")
        self.sparql_update = SPARQLWrapper(f"{self.endpoint}/update")
        
        # Configurar autenticación si es necesario
        if os.getenv('FUSEKI_USER') and os.getenv('FUSEKI_PASSWORD'):
            self.sparql.setCredentials(os.getenv('FUSEKI_USER'), os.getenv('FUSEKI_PASSWORD'))
            self.sparql_update.setCredentials(os.getenv('FUSEKI_USER'), os.getenv('FUSEKI_PASSWORD'))
        
        self.sparql.setReturnFormat(JSON)
        self.sparql_update.setMethod(POST)
        
        # Namespaces
        self.EX = Namespace("http://example.org/movies#")
        self.RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        
        # Inicializar el dataset y la ontología
        self._init_dataset()
        self._init_ontology()

    def _init_dataset(self):
        """Inicializa el dataset en Fuseki si no existe"""
        try:
            # Verificar si el dataset existe
            response = requests.get(f"{self.admin_endpoint}/$/datasets")
            datasets = response.json()
            
            if not any(ds.get('ds.name') == self.dataset_name for ds in datasets.get('datasets', [])):
                logger.info(f"Creando dataset '{self.dataset_name}'...")
                # Crear el dataset
                create_url = f"{self.admin_endpoint}/$/datasets"
                response = requests.post(create_url, data={'dbName': self.dataset_name, 'dbType': 'tdb2'})
                if response.status_code == 200:
                    logger.info(f"Dataset '{self.dataset_name}' creado exitosamente")
                else:
                    logger.error(f"Error al crear dataset: {response.text}")
        except Exception as e:
            logger.error(f"Error al inicializar dataset: {str(e)}")

    def _init_ontology(self):
        """Inicializa la ontología básica si no existe"""
        try:
            # Verificar si ya existe la clase Movie
            check_query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX ex: <http://example.org/movies#>
            ASK WHERE { ex:Movie rdf:type rdfs:Class }
            """
            self.sparql.setQuery(check_query)
            result = self.sparql.query().convert()
            
            if not result.get('boolean', False):
                # Crear la ontología básica
                update_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX ex: <http://example.org/movies#>
                
                INSERT DATA {
                    ex:Movie rdf:type rdfs:Class ;
                        rdfs:label "Movie" ;
                        rdfs:comment "A motion picture or film" .
                        
                    ex:User rdf:type rdfs:Class ;
                        rdfs:label "User" ;
                        rdfs:comment "A user of the movie recommendation system" .
                        
                    ex:title rdf:type rdf:Property ;
                        rdfs:domain ex:Movie ;
                        rdfs:range rdfs:Literal .
                        
                    ex:director rdf:type rdf:Property ;
                        rdfs:domain ex:Movie ;
                        rdfs:range rdfs:Literal .
                        
                    ex:genre rdf:type rdf:Property ;
                        rdfs:domain ex:Movie ;
                        rdfs:range rdfs:Literal .
                        
                    ex:rating rdf:type rdf:Property ;
                        rdfs:domain ex:Movie ;
                        rdfs:range rdfs:Literal .
                        
                    ex:hasFavorite rdf:type rdf:Property ;
                        rdfs:domain ex:User ;
                        rdfs:range ex:Movie .
                }
                """
                self.sparql_update.setQuery(update_query)
                self.sparql_update.query()
                logger.info("Ontología básica inicializada")
        except Exception as e:
            logger.error(f"Error al inicializar ontología: {str(e)}")
            raise

    def add_movie(self, movie_data):
        """Añade una película al triplestore usando SPARQL Update"""
        try:
            movie_id = movie_data['id']
            
            # Escapar caracteres especiales en strings
            title = movie_data['title'].replace('"', '\\"')
            director = movie_data['director'].replace('"', '\\"')
            genre = movie_data['genre']
            rating = float(movie_data['rating'])
            
            update_query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ex: <http://example.org/movies#>
            
            INSERT DATA {{
                ex:movie_{movie_id} rdf:type ex:Movie ;
                          ex:title "{title}" ;
                          ex:director "{director}" ;
                          ex:genre "{genre}" ;
                          ex:rating {rating} .
            }}
            """
            self.sparql_update.setQuery(update_query)
            self.sparql_update.query()
            logger.info(f"Película agregada: {title} (ID: {movie_id})")
            return True
        except Exception as e:
            logger.error(f"Error al agregar película: {str(e)}")
            raise

    def get_movie_details(self, movie_id):
        """Obtiene los detalles de una película específica"""
        try:
            query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ex: <http://example.org/movies#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            
            SELECT ?title ?director ?genre ?rating
            WHERE {{
                ex:movie_{movie_id} rdf:type ex:Movie ;
                                   ex:title ?title ;
                                   ex:director ?director ;
                                   ex:genre ?genre ;
                                   ex:rating ?rating .
            }}
            """
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            
            if not results["results"]["bindings"]:
                logger.warning(f"No se encontró la película con ID: {movie_id}")
                return None
                
            logger.info(f"Detalles obtenidos para película ID: {movie_id}")
            return results["results"]["bindings"][0]
        except Exception as e:
            logger.error(f"Error al obtener detalles de película: {str(e)}")
            return None

    def add_favorite_movie(self, user_id, movie_id):
        """Registra una película como favorita para un usuario"""
        try:
            # Primero asegurarse de que el usuario existe
            self._ensure_user_exists(user_id)
            
            update_query = f"""
            PREFIX ex: <http://example.org/movies#>
            
            INSERT DATA {{
                ex:user_{user_id} ex:hasFavorite ex:movie_{movie_id} .
            }}
            """
            self.sparql_update.setQuery(update_query)
            self.sparql_update.query()
            logger.info(f"Película {movie_id} agregada a favoritos del usuario {user_id}")
        except Exception as e:
            logger.error(f"Error al agregar favorito: {str(e)}")
            raise

    def _ensure_user_exists(self, user_id):
        """Asegura que el usuario existe en el sistema"""
        try:
            check_query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ex: <http://example.org/movies#>
            ASK WHERE {{ ex:user_{user_id} rdf:type ex:User }}
            """
            self.sparql.setQuery(check_query)
            result = self.sparql.query().convert()
            
            if not result.get('boolean', False):
                update_query = f"""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX ex: <http://example.org/movies#>
                INSERT DATA {{
                    ex:user_{user_id} rdf:type ex:User .
                }}
                """
                self.sparql_update.setQuery(update_query)
                self.sparql_update.query()
                logger.info(f"Usuario {user_id} creado")
        except Exception as e:
            logger.error(f"Error al verificar/crear usuario: {str(e)}")
            raise

    def get_user_preferences(self, user_id):
        """Obtiene las preferencias del usuario basadas en sus películas favoritas"""
        try:
            query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ex: <http://example.org/movies#>
            
            SELECT ?genre (COUNT(?movie) as ?count)
            WHERE {{
                ex:user_{user_id} ex:hasFavorite ?movie .
                ?movie ex:genre ?genre .
            }}
            GROUP BY ?genre
            ORDER BY DESC(?count)
            """
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            return results["results"]["bindings"]
        except Exception as e:
            logger.error(f"Error al obtener preferencias: {str(e)}")
            return []

    def get_similar_movies(self, user_id, genres, directors, min_rating=3.0):
        """Encuentra películas similares basadas en géneros y directores preferidos, excluyendo favoritas"""
        try:
            genres_filter = " || ".join([f"?genre = '{g}'" for g in genres]) if genres else "true"
            directors_filter = " || ".join([f"?director = '{d}'" for d in directors]) if directors else "true"
            
            query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ex: <http://example.org/movies#>
            
            SELECT DISTINCT ?movie ?title ?genre ?director ?rating
            WHERE {{
                ?movie rdf:type ex:Movie ;
                       ex:title ?title ;
                       ex:genre ?genre ;
                       ex:director ?director ;
                       ex:rating ?rating .
                
                # Excluir películas que ya son favoritas del usuario
                FILTER NOT EXISTS {{
                    ex:user_{user_id} ex:hasFavorite ?movie
                }}
                
                FILTER(({genres_filter}) || ({directors_filter}))
                FILTER(?rating >= {min_rating})
            }}
            ORDER BY DESC(?rating)
            LIMIT 10
            """
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            return results["results"]["bindings"]
        except Exception as e:
            logger.error(f"Error al obtener películas similares: {str(e)}")
            return []

    def get_favorite_movies(self, user_id):
        """Obtiene las películas favoritas de un usuario"""
        try:
            query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ex: <http://example.org/movies#>
            
            SELECT DISTINCT ?movie ?title ?genre ?director ?rating
            WHERE {{
                ex:user_{user_id} ex:hasFavorite ?movie .
                ?movie rdf:type ex:Movie ;
                       ex:title ?title ;
                       ex:genre ?genre ;
                       ex:director ?director ;
                       ex:rating ?rating .
            }}
            ORDER BY ?title
            """
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            return results["results"]["bindings"]
        except Exception as e:
            logger.error(f"Error al obtener películas favoritas: {str(e)}")
            return []

    def is_favorite_movie(self, user_id, movie_id):
        """Verifica si una película es favorita para un usuario"""
        try:
            query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ex: <http://example.org/movies#>
            
            ASK {{
                ex:user_{user_id} ex:hasFavorite ex:movie_{movie_id}
            }}
            """
            self.sparql.setQuery(query)
            result = self.sparql.query().convert()
            return result.get('boolean', False)
        except Exception as e:
            logger.error(f"Error al verificar película favorita: {str(e)}")
            return False

    def get_all_movies(self):
        """Obtiene todas las películas almacenadas"""
        try:
            query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ex: <http://example.org/movies#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            
            SELECT DISTINCT ?movie ?title ?director ?genre ?rating
            WHERE {
                ?movie rdf:type ex:Movie ;
                       ex:title ?title ;
                       ex:director ?director ;
                       ex:genre ?genre ;
                       ex:rating ?rating .
            }
            ORDER BY DESC(?rating) ?title
            """
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            
            if not results["results"]["bindings"]:
                logger.info("No se encontraron películas en la base de datos")
                return []
                
            logger.info(f"Se encontraron {len(results['results']['bindings'])} películas")
            return results["results"]["bindings"]
        except Exception as e:
            logger.error(f"Error al obtener todas las películas: {str(e)}")
            return []

    def remove_favorite_movie(self, user_id, movie_id):
        """Elimina una película de los favoritos de un usuario"""
        try:
            update_query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ex: <http://example.org/movies#>
            
            DELETE DATA {{
                ex:user_{user_id} ex:hasFavorite ex:movie_{movie_id} .
            }}
            """
            self.sparql_update.setQuery(update_query)
            self.sparql_update.query()
            logger.info(f"Película {movie_id} eliminada de favoritos del usuario {user_id}")
        except Exception as e:
            logger.error(f"Error al eliminar favorito: {str(e)}")
            raise 