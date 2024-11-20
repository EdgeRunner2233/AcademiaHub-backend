import json
import unittest
from src import create_app
from src.extensions import db


class ApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
        cls.test_db = db
        cls.app_context = cls.app.app_context()
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context.push()

        self.test_db.create_all()

    def tearDown(self):
        self.test_db.session.remove()
        self.test_db.drop_all()

        self.app_context.pop()

    def test_app_exist(self):
        self.assertIsNotNone(self.app)

    def test_app_is_testing(self):
        self.assertTrue(self.app.testing)
        self.assertTrue(self.app.config["TESTING"])

    def test_api_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.data)
        self.assertIn("success", payload)
        self.assertIn("code", payload)
        self.assertIn("message", payload)
        self.assertIn("data", payload)

        self.assertEqual(payload["success"], True)
        self.assertEqual(payload["code"], 0)
