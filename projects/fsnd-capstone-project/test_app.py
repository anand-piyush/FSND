import unittest
from app import app
from models import setup_db, database_path
import json
from flask_sqlalchemy import SQLAlchemy
from models import Actors, Movies
from flask import Flask



EXECUTIVE_PROD_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1qWXNIOW04ajFZSE83c21TbkprNiJ9.eyJpc3MiOiJodHRwczovL2lhbWdtdC5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjExOGJhNzk3YzcxYzQwMDY5NDY0YjI3IiwiYXVkIjoiY2FzdGluZ19hZ2VuY3kiLCJpYXQiOjE2MzI0OTU0OTMsImV4cCI6MTYzMjUwMjY5MywiYXpwIjoiWWJ4RXFXVDNUTEhEbmprNVFxNlFVQVZHcEtwTjJEcXoiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphY3RvcnMiLCJkZWxldGU6bW92aWVzIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiLCJwYXRjaDphY3RvcnMiLCJwYXRjaDptb3ZpZXMiLCJwb3N0OmFjdG9ycyIsInBvc3Q6bW92aWVzIl19.B5YyvHU5A3sqitrHP86DZB1-4fcJ2ev1lpA6QIiQHKVleX3FPnxyAwnGkcEckbbN_mbokZD8cP7AcYBanx65DaZFOiuj6_RsngL_2Bg_7GsTlSCV4BBqZ-dqrT51lRwpXPKz1JQjlq3U7cmQbwnPE2TnukyTeIM1Avkfc7Icbdrepygg3Nbq3LI5ypfpw2Cr7mm9z7FyucQFpV1ApEVw3Xtb6AiMyt4Mh-AdZRsSMCdtPKBPqktZ6FO5xB6_73DxgkYzh3yuGlcr_97vLBaQU2G-MiL7uyIl55uUX3-LMJVW8HNvzxRLq_VshzNEAhh8T8ZO7Y1HkJ37cyM2OLEYrw'


class CastingAgencyTestCase(unittest.TestCase):
    """This class represents the trivia test case"""


    def setUp(self):
        """Define test variables and initialize app."""

        self.app = app
        self.database_path = database_path
        # setup_db(self.app, database_path=self.database_path)
        self.exec_prod = EXECUTIVE_PROD_TOKEN
        app.config['TESTING'] = True
        self.client = self.app.test_client

        self.new_actor = {
            "firstname": "Anya",
            "lastname": "Taylor-Joy",
            "age": 24,
            "gender": "Female"
        }
        self.update_actor = {
            "lastname": "Anand"
        }
        self.new_movie = {
            "title": "Stranger Things Creation",
            "release_date": "2021-02-08"
        }
        self.update_movie = {
            "description": "A movie about strange things"
        }

        # binds the app to the current context
        # with self.app.app_context():
            # self.db = SQLAlchemy()
            # self.db.init_app(self.app)
            # create all tables
            # self.db.create_all()


    def tearDown(self):
        """Executed after reach test"""
        pass


    def test_get_paginated_actors(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)

        print('------------------------GET all actors test -----------------------')
        # print(data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['actors']), 0)

    
    def test_get_actors_with_non_integer_page_argument(self):
        res = self.client().get('/actors?page=abc')
        data = json.loads(res.data)

        print('---------GET actors using a non-integer page argument----------------')
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])


    def test_get_paginated_movies(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)

        print('------------------------GET all movies test--------------------------')
        # print(data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['movies']), 0)


    def test_get_movies_with_non_integer_page_argument(self):
        res = self.client().get('/movies?page=abc')
        data = json.loads(res.data)

        print('---------GET movies using a non-integer page argument----------------')
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])

    
    def test_post_actors(self):
        new_actor = self.new_actor
        res = self.client().post('/actors',
                                    headers={
                                    'Authorization': 'Bearer ' + self.exec_prod
                                    },
                                    json=new_actor
        )

        data = json.loads(res.data)
        print('------------POST a new actor with executive permissions---------------')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])


    def test_post_actors_without_permission(self):
        new_actor = self.new_actor
        res = self.client().post('/actors',
                                    json=new_actor
        )

        data = json.loads(res.data)
        print('------------POST a new actor without executive permissions---------------')
        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])


    def test_post_movies(self):
        new_movie = self.new_movie
        res = self.client().post('/movies',
                                    headers={
                                    'Authorization': 'Bearer ' + self.exec_prod
                                    },
                                    json=new_movie
        )

        data = json.loads(res.data)
        print('------------POST a new movie with executive permissions---------------')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])


    def test_post_movies_without_permission(self):
        new_movie = self.new_movie
        res = self.client().post('/movies',
                                    json=new_movie
        )

        data = json.loads(res.data)
        print('------------POST a new movie without executive permissions---------------')
        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])


    def test_patch_actors(self):
        update_actor = self.update_actor
        res = self.client().patch('/actors/47',
                                    headers={
                                    'Authorization': 'Bearer ' + self.exec_prod,
                                    'Content-Type': 'application/json'
                                    },
                                    json=update_actor
        )

        data = json.loads(res.data)
        print('------------PATCH a new actor with executive permissions---------------')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])


    def test_patch_actors_without_permission(self):
        update_actor = self.update_actor
        res = self.client().patch('/actors/47',
                                    json=update_actor
        )

        data = json.loads(res.data)
        print('------------PATCH a new actor without executive permissions---------------')
        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])

    
    def test_patch_movies(self):
        update_movie = self.update_movie
        res = self.client().patch('/movies/32',
                                    headers={
                                    'Authorization': 'Bearer ' + self.exec_prod
                                    },
                                    json=update_movie
        )

        data = json.loads(res.data)
        print('------------PATCH a new movie with executive permissions---------------')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])


    def test_patch_movies_without_permission(self):
        update_movie = self.update_movie
        res = self.client().patch('/movies/32',
                                    json=update_movie
        )

        data = json.loads(res.data)
        print('------------PATCH a new movie without executive permissions---------------')
        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])

    def test_delete_actors(self):
        res = self.client().delete('/actors/12',
                                    headers={
                                    'Authorization': 'Bearer ' + self.exec_prod
                                    },
        )

        data = json.loads(res.data)
        print('------------DELETE an actor with executive permissions---------------')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])


    def test_delete_actors_without_permission(self):
        res = self.client().delete('/actors/12')

        data = json.loads(res.data)
        print('------------DELETE an actor without executive permissions---------------')
        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])


    def test_delete_movies(self):
        res = self.client().delete('/movies/18',
                                    headers={
                                    'Authorization': 'Bearer ' + self.exec_prod
                                    },
        )

        data = json.loads(res.data)
        print('------------DELETE a movie with executive permissions---------------')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])


    def test_delete_movies_without_permission(self):
        update_movie = self.update_movie
        res = self.client().delete('/movies/18')

        data = json.loads(res.data)
        print('------------DELETE a movie without executive permissions---------------')
        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()