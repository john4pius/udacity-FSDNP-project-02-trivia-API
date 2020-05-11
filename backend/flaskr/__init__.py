import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after
    completing the TODOs
    '''
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = list(map(Category.format,
                              Category.query.order_by(
                                Category.id.asc()).all()))
        data = {}
        for category in categories:
            data.update({category["id"]: category["type"]})

        return jsonify({
            "success": True,
            "categories": data
            })

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for
    three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = list(map(Question.format, Question.query.all()))
        total_questions = len(questions)
        questions = questions[start:end]

        categories = get_categories().get_json()["categories"]

        return jsonify({
            "success": True,
            "questions": questions,
            "total_questions": total_questions,
            "current_category": None,
            "categories": categories,
        })

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will
    be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        error = False
        try:
            question = Question.query.get(question_id)
            if not question:
                abort(404)
            question.delete()
        except Exception:
            error = True
            db.session.rollback()
            print(exc.info())
        finally:
            db.session.close()
            if error:
                abort(500)
            else:
                return jsonify({
                    "success": True,
                    "deleted_question": question_id
                    })

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the
    last page
    of the questions list in the "List" tab.
    '''

    @app.route("/questions", methods=["POST"])
    def new_question():
        data = request.get_json()
        if "searchTerm" in data:
            questions = Question.query.filter(
                func.lower(Question.question)
                .like("%{}%".format(data["searchTerm"].lower()))).all()

            formatted_questions = list(map(Question.format, questions))
            return jsonify({
              "questions": formatted_questions,
              "total_questions": len(formatted_questions),
              "current_category": None
              })

        else:
            if not (
                data["question"] and
                data["answer"] and
                data["category"] and
                data["difficulty"]
            ):
                abort(422)
                error = False
            try:
                question = Question(
                    question=data["question"],
                    answer=data["answer"],
                    category=data["category"],
                    difficulty=data["difficulty"]
                )
                question.insert()

            except Exception:
                error = True
                db.session.rollback()
                print(exc.info())

            finally:
                db.session.close()
                if error:
                    abort(500)
                else:
                    return jsonify({
                        "success": True
                    })

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        searchTerm = request.get_json()['searchTerm']
        data_searched = Question.query.filter(
            Question.question.ilike('%{}%'.format(searchTerm))).all()
        formatted_questions = paginate_questions(request, data_searched)

        category_all = Category.query.all()
        categories = [category.format() for category in category_all]
        formatted_categories = {
            k: v for category in categories for k, v in category.items()
        }
        return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions_found': len(data_searched),
          'current_category': "",
          'categories': formatted_categories
        })

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_category(category_id):
        questions = list(
            map(
                Question.format,
                Question.query.filter(
                    (Question.category).like("%{}%".format(category_id))
                ).all(),
            )
        )

        category = Category.query.get(category_id)
        if not category:
            abort(404)

        return jsonify({
            "questions": questions,
            "total_questions": len(questions),
            "current_category": category_id,
            })

    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''

    @app.route("/quizzes", methods=["POST"])
    def get_quiz():
        response_quiz = request.get_json()
        previous_questions = response_quiz['previous_questions']
        category_id = response_quiz["quiz_category"]["id"]
        if category_id == 0:
            if previous_questions is None:
                questions = Question.query.all()
            else:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()

        else:
            if previous_questions is None:
                questions = Question.query.filter(
                    Question.category == category_id).all()
            else:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions),
                    Question.category == category_id).all()

        if len(questions) == 0:
            return jsonify({'question': None})

        next_question = random.choice(questions).format()
        print(next_question)
        if next_question is None:
            next_question = False

        return jsonify({
            'success': True,
            'question': next_question
        })

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad request."
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
          "success": False,
          "error": 404,
          "message": "Not found."
          }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
          "success": False,
          "error": 422,
          "message": "We couldn't process your request."
        }), 422

    @app.errorhandler(500)
    def unprocessable(error):
        return jsonify({
          "success": False,
          "error": 500,
          "message": "Something went wrong."
          }), 500

    return app
