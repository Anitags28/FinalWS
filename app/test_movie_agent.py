import unittest
from unittest.mock import Mock, patch
from movie_agent import MovieAgent
from sparql_manager import SPARQLManager

class TestMovieAgent(unittest.TestCase):
    def setUp(self):
        self.movie_agent = MovieAgent()
        self.mock_movie_data = {
            'title': {'value': 'Test Movie'},
            'director': {'value': 'Test Director'},
            'genre': {'value': 'Action'},
            'rating': {'value': '4.5'}
        }

    @patch.object(SPARQLManager, 'get_movie_details')
    def test_generate_opinion(self, mock_get_details):
        mock_get_details.return_value = self.mock_movie_data
        opinion = self.movie_agent.generate_opinion('test_id')
        
        self.assertIn('Test Movie', opinion)
        self.assertIn('Test Director', opinion)
        self.assertIn('acción', opinion.lower())

    @patch.object(SPARQLManager, 'get_user_preferences')
    @patch.object(SPARQLManager, 'get_similar_movies')
    def test_get_recommendations(self, mock_similar_movies, mock_preferences):
        # Simular preferencias del usuario
        mock_preferences.return_value = [
            {'genre': {'value': 'Action'}, 'count': {'value': '2'}},
            {'genre': {'value': 'Drama'}, 'count': {'value': '1'}}
        ]
        
        # Simular películas similares
        mock_similar_movies.return_value = [{
            'movie': {'value': 'movie_1'},
            'title': {'value': 'Test Movie'},
            'director': {'value': 'Test Director'},
            'genre': {'value': 'Action'},
            'rating': {'value': '4.5'}
        }]

        recommendations = self.movie_agent.get_recommendations('test_user')
        
        self.assertTrue(len(recommendations) > 0)
        self.assertEqual(recommendations[0]['title'], 'Test Movie')
        self.assertEqual(recommendations[0]['rating'], 4.5)

    def test_get_genre_description(self):
        description = self.movie_agent._get_genre_description('Action')
        self.assertIn('acción', description.lower())
        
        description = self.movie_agent._get_genre_description('Unknown')
        self.assertIn('género Unknown', description)

    def test_get_rating_description(self):
        description = self.movie_agent._get_rating_description(4.5)
        self.assertIn('obra maestra', description.lower())
        
        description = self.movie_agent._get_rating_description(2.5)
        self.assertIn('algunos espectadores', description.lower())

class TestSPARQLManager(unittest.TestCase):
    def setUp(self):
        self.sparql_manager = SPARQLManager()

    @patch('SPARQLWrapper.SPARQLWrapper.query')
    def test_get_movie_details(self, mock_query):
        mock_response = Mock()
        mock_response.convert.return_value = {
            'results': {
                'bindings': [{
                    'title': {'value': 'Test Movie'},
                    'director': {'value': 'Test Director'},
                    'genre': {'value': 'Action'},
                    'rating': {'value': '4.5'}
                }]
            }
        }
        mock_query.return_value = mock_response

        result = self.sparql_manager.get_movie_details('test_id')
        self.assertEqual(result['title']['value'], 'Test Movie')
        self.assertEqual(result['rating']['value'], '4.5')

    @patch('SPARQLWrapper.SPARQLWrapper.query')
    def test_get_user_preferences(self, mock_query):
        mock_response = Mock()
        mock_response.convert.return_value = {
            'results': {
                'bindings': [{
                    'genre': {'value': 'Action'},
                    'count': {'value': '2'}
                }]
            }
        }
        mock_query.return_value = mock_response

        result = self.sparql_manager.get_user_preferences('test_user')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['genre']['value'], 'Action')
        self.assertEqual(result[0]['count']['value'], '2')

if __name__ == '__main__':
    unittest.main() 