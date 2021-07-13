import os
import random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

from models import setup_db, Question, Category
from flaskr.utils import paginate

# export FLASK_APP=flaskr
# export FLASK_ENV=development
# flask run --reload


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  
  # TODo Done : COMMENT OR DELETE THE BELOW METHOD WHEN PROJECT COMPLETES
  # @app.route('/api/v1.0/')
  # @app.route('/')
  # def main():
  #   return('hello piyush')


  '''
  @TODo DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the Todos
  '''
  CORS(app, resources={r'/api/v1.0/*':{"origins":"*"}})


  '''
  @TODo DONE: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
    return response

  def query_categories():
    '''
    method to query categories from db
    '''
    categories = Category.query.all()
    cat_dict = {cat.id:cat.type for cat in categories}
    return cat_dict

  '''
  @TODo Done
  '''
  @app.route('/api/v1.0/categories')
  def get_categories():
    ''' 
    an endpoint to handle GET requests 
    for all available categories.
    '''
    try:
      cat_dict = query_categories()
      return jsonify({
          "success": True,
          "categories": cat_dict
      })
    except Exception as e:
      print(e)
      abort(500)  
    

  

  '''
  @TODo Done: 
  '''
  @app.route('/api/v1.0/questions', methods=['GET'])
  def get_questions():
    '''
    an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    questions = Question.query.all()
    total_questions = len(questions)

    ques_list = paginate(request, questions)
    cat_dict = query_categories()
    
    if len(ques_list) == 0:
        # page requested is beyond the available pages
        abort(404)

    return jsonify({
        'success': True,
        'questions': ques_list,
        'total_questions': total_questions,
        'categories': cat_dict,
        'current_category': None
    })

  '''
  @TODo Done: 
  '''
  @app.route("/api/v1.0/questions/<int:question_id>", methods=['DELETE'])
  def delete_question(question_id):
    """
    an endpoint to DELETE question using a question ID. 
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    """
    question = Question.query.get(question_id)
    success = False
    if not question:
      abort(404)
    else:
      try:
        question.delete()
        success = True
      except:
        # unable to process
        abort(422)
      return jsonify({
                    'success': success,
                    'deleted': question_id
                })




  '''
  @TODo Done:
  '''

  @app.route('/api/v1.0/questions', methods=['POST'])
  def add_question():
    '''
    an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    if searchTerm is given, a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    form_data = request.json
    if "searchTerm" in form_data:
        search_term = form_data['searchTerm'].strip()
        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all() 
        
        # paginate not supported at frontend, so all results returned
        q_list = [q.format() for q in questions]

        return jsonify({
            "success": True,
            "questions": q_list
        })
    
    else:
        if (form_data['question'].strip() == "") or (form_data['answer'].strip() == ""):
            # Empty Values
            abort(400)

        try:
            ques = form_data['question'].strip()
            ans = form_data['answer'].strip()
            cat = form_data['category']
            difficulty = form_data['difficulty']
            new_question = Question(question=ques, answer=ans,category=cat, difficulty=difficulty)
            new_question.insert()
        except:
            abort(422)

        return jsonify({
            "success": True,
            "added": new_question.id
        })

  
  '''
  @TODo Done
  '''

  @app.route('/api/v1.0/categories/<int:cat_id>/questions')
  def get_category_questions(cat_id):
    '''
    GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    questions = Question.query.filter_by(category=str(cat_id)).all()
    ques_list = paginate(request, questions)

    if len(ques_list) == 0: # no questions for the page
        abort(404)

    return jsonify({
        'success': True,
        'questions': ques_list,
        'total_questions': len(questions),
        'categories': Category.query.get(cat_id).format(),
        'current_category': cat_id
    })


  '''
  @TODo Done
  '''

  @app.route('/api/v1.0/quizzes', methods=['POST'])
  def quiz():
    '''
    a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
    category 0 means all

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    try:
      request_data = request.json
      request_cat = request_data['quiz_category']['id']
      prev_ques = request_data['previous_questions']    
    except:
      abort(400)

    questions = Question.query.filter_by(category=str(request_cat)).all() if request_cat \
                else Question.query.all()
    questions = [ques.format() for ques in questions]
    
    new_ques = [ques for ques in questions if ques['id'] not in prev_ques]
    # if new ques are none, means game is over
    if not new_ques:
        return jsonify({
            'success': True
        })

    # else, pick a random question from the new set
    question = random.choice(new_ques)
    return jsonify({
        'success': True,
        'question': question
    })

  '''
  @TODo Done: 
  Error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }),400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }),404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }),422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }),500

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Requested Method Not Allowed"
    }),405
  
  return app

    