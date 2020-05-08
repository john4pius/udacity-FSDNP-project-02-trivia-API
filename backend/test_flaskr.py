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
            
        self.demo = {
            "question": "Whats my name?",
            "answer": "John",
            "difficulty": 1,
            "category": "2",
        }    
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    def test_get_questions(self):
    
        response = self.client().get("/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_get_categories(self):

        response = self.client().get("/categories")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_get_questions_category(self):

        response = self.client().get("/categories/2/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_new_question(self):

        questions_before = Question.query.all()

        response = self.client().post("/questions", json=self.demo)

        data = json.loads(response.data)

        questions_after = Question.query.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(questions_after) - len(questions_before) == 1)

    def test_search_questions(self):

        response = self.client().post("/questions",
                                      json={"searchTerm": "1990"})

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["questions"]), 1)
        self.assertEqual(data["questions"][0]["id"], 6)

    def test_get_questions_category_error(self):

        response = self.client().get("/categories/50/questions")

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_quiz(self):
        response = self.client().post(
            "/quizzes",
            json={
                "previous_questions": [10],
                "quiz_category": {"type": "Sport", "id": "6"},
            },
        )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["question"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()