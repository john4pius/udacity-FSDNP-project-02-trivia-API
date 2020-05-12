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
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name
        )
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
    Write at least one test for each test for
    successful operation and for expected errors.
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

    def test_get_categories_fail(self):

        response = self.client().get("/categories/8")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_get_questions_category(self):

        response = self.client().get("/categories/2/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_get_questions_category_fail(self):

        respond = self.client().get("/categories/0/questions")
        data = json.loads(respond.data)

        self.assertEqual(respond.status_code, 400)
        self.assertEqual(data["success"], False)

    def test_new_question(self):

        response = self.client().post(
            "/questions",
            data=json.dumps(self.demo),
            content_type="application/json"
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data["question"])

    def test_new_question_fail(self):
        response = self.client().post(
            "/questions",
            data=json.dumps({}),
            content_type="application/json"
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)

    def test_search_questions_fail(self):

        request_data = {"searchTerm": "what"}
        response = self.client().post(
            "/search",
            data=json.dumps(request_data),
            content_type="application/json"
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_quiz(self):
        response = self.client().post(
            "/quizzes",
            json={
                "previous_questions": [20, 21],
                "quiz_category": {"type": "Science", "id": "1"}
            }
        )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
        self.assertEqual(data["question"]["category"], 1)

        self.assertNotEqual(data["question"]["id"], 20)
        self.assertNotEqual(data["question"]["id"], 21)

    def test_get_quiz_fail(self):
        response = self.client().post(
            "/quizzes",
            data=json.dumps({}),
            content_type="application/json"
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data["success"], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
