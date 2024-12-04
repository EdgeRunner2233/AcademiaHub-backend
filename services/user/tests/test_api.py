import json
import unittest
from src import create_app
from src.model import User
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

    def register(self, email=None, nickname=None, password=None):
        """
        Register a user.

        Args:
            email (str): The email of the user.
            nickname (str): The nickname of the user.
            password (str): The password of the user.

        Returns:
            dict: The response payload.
        """

        email = email or "test@email.email"
        nickname = nickname or "test"
        password = password or "test_password"
        response = self.client.post(
            "/api/user/register",
            data=json.dumps(
                {
                    "email": email,
                    "nickname": nickname,
                    "password": password,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload: dict = json.loads(response.data)

        return payload

    def login(self, email=None, password=None):
        """
        Login a user.

        Args:
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            dict: The response payload.
        """

        email = email or "test@email.email"
        password = password or "test_password"
        response = self.client.post(
            "/api/user/login",
            data=json.dumps(
                {
                    "email": email,
                    "password": password,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload: dict = json.loads(response.data)

        return payload

    def test_app_exist(self):
        self.assertIsNotNone(self.app)

    def test_app_is_testing(self):
        self.assertTrue(self.app.testing)
        self.assertTrue(self.app.config["TESTING"])

    def test_nonexistent_url(self):
        response = self.client.get("/api/user/nonexistent")
        self.assertEqual(response.status_code, 404)

    def test_api_health(self):
        response = self.client.get("/api/user/health")
        self.assertEqual(response.status_code, 200)

        payload: dict = json.loads(response.data)
        self.assertIn("success", payload)
        self.assertIn("code", payload)
        self.assertIn("message", payload)
        self.assertIn("data", payload)

        self.assertEqual(payload["success"], True)
        self.assertEqual(payload["code"], 0)

    def test_api_login(self):
        response = self.register()
        response = self.client.post(
            "/api/user/login",
            data=json.dumps(
                {
                    "email": "test@email.email",
                    "password": "test_password",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        payload: dict = json.loads(response.data)
        self.assertIn("success", payload)
        self.assertIn("code", payload)
        self.assertIn("message", payload)
        self.assertIn("data", payload)

        self.assertEqual(payload["success"], True)
        self.assertEqual(payload["code"], 300)

        user_id = payload["data"]["id"]
        token = payload["data"]["token"]
        user = User.get_by_id(user_id)
        self.assertIsNotNone(user)
        self.assertTrue(user.verify_token(token)[0])

    def test_api_register(self):
        response = self.client.post(
            "/api/user/register",
            data=json.dumps(
                {
                    "email": "test@email.email",
                    "nickname": "test",
                    "password": "test_password",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        payload: dict = json.loads(response.data)
        self.assertIn("success", payload)
        self.assertIn("code", payload)
        self.assertIn("message", payload)
        self.assertIn("data", payload)

        self.assertEqual(payload["success"], True)
        self.assertEqual(payload["code"], 310)

        user_id = payload["data"]["id"]
        token = payload["data"]["token"]
        user = User.get_by_id(user_id)
        self.assertIsNotNone(user)
        self.assertTrue(user.verify_token(token)[0])
