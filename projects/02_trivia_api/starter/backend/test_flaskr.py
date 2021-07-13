import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODo Done
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_custom_404_sent_if_requesting_an_invalid_page(self):
        res = self.client().get('/api/v2.0/categories')
        data = json.loads(res.data)

        self.assertNotEqual(res.status_code, 200)  
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_get_categories(self):
        """Gets the /api/categories endpoint and checks valid results"""
        res = self.client().get('/api/v1.0/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)

    def test_custom_404_sent_if_requesting_non_existing_category(self):
        res = self.client().get('/api/v1.0/categories/9999/questions')
        data = json.loads(res.data)

        self.assertNotEqual(res.status_code, 200)  
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')
    
    def test_get_questions_by_category(self):
        res = self.client().get('/api/v1.0/categories/1/questions')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['current_category'], 1)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']), 3)
        self.assertEqual(data['total_questions'], len(data['questions']))

    def test_get_all_questions(self):
        res = self.client().get('/api/v1.0/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['questions'][0]['id'], 5)

    def test_pagination(self):
        res = self.client().get('/api/v1.0/questions?page=2')
        data = json.loads(res.data)

        # page 2 should have only 9 questions, as total its 19
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(len(data['questions']), 9)     
        self.assertEqual(data['questions'][0]['id'], 15)

    def test_requested_page_doesnt_exist(self):
        res = self.client().get('/api/v1.0/questions?page=1000')
        data = json.loads(res.data)

        self.assertNotEqual(res.status_code, 200)  
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_delete_question(self):
        # test originally 19
        all_questions = Question.query.all()
        self.assertEqual(len(all_questions), 19)

        # Create a dummy question to delete
        new_question = Question(question="dummy question", answer="dummy answer", category=2, difficulty=1)
        new_question.insert()
        nq_id = new_question.id

        # Test if question added successfully
        all_questions = Question.query.all()
        self.assertEqual(len(all_questions), 20)    # 19 originally were there

        # Test Delete
        res = self.client().delete(f'/api/v1.0/questions/{nq_id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], nq_id)

        # Test if delete is persisted
        all_questions = Question.query.all()
        self.assertEqual(len(all_questions), 19)    # 19 originally were there

    def test_invalid_delete_question(self):
        """Try to delete a question that doesn't exist, should get a 404 error"""
        res = self.client().delete(f'/api/questions/1000')
        data = json.loads(res.data)

        self.assertNotEqual(res.status_code, 200)  
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_post_new_question(self):
        # count the num of ques originally in db
        # add 1 ques
        # check if count increased
        # revert

        all_questions = Question.query.all()
        orig_num_questions = len(all_questions)

        new_question = {
            'question': 'new question',
            'answer': 'new answer',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/api/v1.0/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        new_q_id = data['added']
        
        # Count that a new question was added, should have 20 after add
        all_questions = Question.query.all()
        self.assertEqual(len(all_questions), orig_num_questions + 1)    # 19 +1 should be now

        # Delete question from database again with another client request.  
        # API returns the primary key
        res = self.client().delete(f'/api/v1.0/questions/{new_q_id}')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], new_q_id)
        self.assertNotEqual(res.status_code, 404)  
        self.assertEqual(res.status_code, 200)

    def test_post_empty_question(self):
        empty_question = {
            "question": "          ",
            "answer": "           ",
            "category": "6",
            "difficulty": 1
        }
        res = self.client().post('/api/v1.0/questions', json=empty_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'Bad Request')
    
    def test_question_search(self):
        res = self.client().post('/api/v1.0/questions', json={"searchTerm": "  Peanut  "})   # Who invented Peanut Butter?
        data_uncased = json.loads(res.data)

        self.assertEqual(data_uncased['success'], True)
        self.assertEqual(len(data_uncased['questions']), 1)
        self.assertEqual(data_uncased['questions'][0]['id'], 12)

        # test if its case independent
        res = self.client().post('/api/v1.0/questions', json={"searchTerm": "  PeaNUT  "})   # Who invented Peanut Butter?
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['questions'][0]['id'], 12)
        self.assertEqual(len(data['questions']), len(data_uncased['questions']))

    def test_question_search_with_more_than_1_results(self):
        res = self.client().post('/api/v1.0/questions', json={"searchTerm": "  what  "})   # Who invented Peanut Butter?
        data_uncased = json.loads(res.data)

        self.assertEqual(data_uncased['success'], True)
        self.assertEqual(len(data_uncased['questions']), 8)

    def test_question_search_with_more_than_10_results(self):
        res = self.client().post('/api/v1.0/questions', json={"searchTerm": "  the  "})   # Who invented Peanut Butter?
        data_uncased = json.loads(res.data)

        self.assertEqual(data_uncased['success'], True)
        self.assertEqual(len(data_uncased['questions']), 11) # no pagination

    # taking geography as test for quiz and testing if the user is being served with right questions

    def test_play_quiz_regular_case(self):
        # Test quiz when all 3 questions are left
        res = self.client().post('/api/v1.0/quizzes', json={"previous_questions": [], "quiz_category": {"type": "Geography", "id": "3"}})
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)                 
        self.assertIsNotNone(data['question'])   # questions are returned              
        self.assertEqual(data['question']['category'], 3)      

    def test_play_quiz_when_only_one_question_left_in_category(self):
        # Test quiz when 2 of 3 have been asked and only one choice left i.e. 15
        res = self.client().post('/api/v1.0/quizzes', json={"previous_questions": [13, 14], "quiz_category": {"type": "Geography", "id": "3"}})
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)               
        self.assertEqual(data['question']['id'], 15)            
        
    def test_play_quiz_when_no_questions_left_in_category(self):
        res = self.client().post('/api/v1.0/quizzes', json={"previous_questions": [13, 14, 15], "quiz_category": {"type": "Geography", "id": "3"}})
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)                
        self.assertFalse('question' in data)                    # no key with name question in data as no questions left

    def test_play_quiz_error_case_category_missing(self):
        res = self.client().post('/api/v1.0/quizzes', json={"previous_questions": [13], "quiz_category": {"type": "Geography"}})
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)               
        self.assertEqual(data['error'], 400) 
        self.assertNotEqual(data['error'], 200)      

             
    def test_422_sent_posting_invalid_question_form(self):
        malformed_question = {
            "question": "i am a test ques",
            "answer": "test",
            "category_MALFORMED": "6",
            "difficulty": 1
        }
        res = self.client().post('/api/v1.0/questions', json=malformed_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422) 
        self.assertNotEqual(res.status_code, 200)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_method_not_allowed_requesting_specific_questions_via_get(self):
        # only delete allowed on this
        res = self.client().get('/api/v1.0/questions/1000')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 405)
        self.assertNotEqual(res.status_code, 200)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Requested Method Not Allowed')

    
    

        


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()