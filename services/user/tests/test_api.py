import json
import unittest
from src import create_app
from src.model import User
from fakeredis import FakeRedis
from unittest.mock import patch
from src.extensions import db, mail
from werkzeug.test import TestResponse

test_redis = FakeRedis()


@patch("src.cache.redis", test_redis)
class ApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            MAIL_SUPPRESS_SEND=True,
        )
        cls.test_db = db
        cls.app_context = cls.app.app_context()
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context.push()

        self.test_db.create_all()

    def tearDown(self):
        self.test_db.session.remove()
        self.test_db.drop_all()

        test_redis.flushall()

        self.app_context.pop()

    def check_success_field(self, response: TestResponse):
        self.assertEqual(response.status_code, 200)

        payload: dict = json.loads(response.data)
        self.assertIn("success", payload)
        self.assertIn("code", payload)
        self.assertIn("message", payload)
        self.assertIn("data", payload)

        if payload["success"] == False:
            print("Error: ", payload["message"])
        self.assertEqual(payload["success"], True)

        return payload

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

        email = email or "test@email.testemail"
        nickname = nickname or "test"
        password = password or "test_password"

        response = self.client.post(
            "/api/user/get_verification",
            data={"email": email},
            content_type="multipart/form-data",
        )

        verification_code = test_redis.get(f"vcode#{email}")
        self.assertIsNotNone(verification_code)
        verification_code = verification_code.decode("utf-8")
        self.assertTrue(len(verification_code) > 0)

        response = self.client.post(
            "/api/user/register",
            data={
                "email": email,
                "nickname": nickname,
                "password": password,
                "verification_code": verification_code,
            },
            content_type="multipart/form-data",
        )

        return self.check_success_field(response)

    def login(self, email=None, password=None):
        """
        Login a user.

        Args:
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            dict: The response payload.
        """

        email = email or "test@email.testemail"
        password = password or "test_password"
        response = self.client.post(
            "/api/user/login",
            data={"email": email, "password": password},
            content_type="multipart/form-data",
        )

        return self.check_success_field(response)

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
        payload = self.check_success_field(response)
        self.assertEqual(payload["code"], 0)

    def test_api_get_verification(self):
        verification_code = test_redis.get("vcode#test@email.testemail")
        self.assertIsNone(verification_code)

        with mail.record_messages() as outbox:
            response = self.client.post(
                "/api/user/get_verification",
                data={"email": "test@email.testemail"},
                content_type="multipart/form-data",
            )

            self.assertEqual(len(outbox), 1)

        self.check_success_field(response)

        v_code = test_redis.get("vcode#test@email.testemail")
        self.assertIsNotNone(v_code)
        v_code = v_code.decode("utf-8")
        self.assertTrue(len(v_code) > 0)

        self.assertEqual(outbox[0].subject, f"[AcademiaHub] 验证码: {v_code}")

    def test_api_login(self):
        response = self.register()
        response = self.client.post(
            "/api/user/login",
            data={"email": "test@email.testemail", "password": "test_password"},
            content_type="multipart/form-data",
        )

        payload = self.check_success_field(response)
        self.assertEqual(payload["code"], 300)

        user_id = payload["data"]["id"]
        token = payload["data"]["token"]
        user = User.get_by_id(user_id)
        self.assertIsNotNone(user)
        self.assertTrue(user.verify_token(token)[0])

    def test_api_register(self):
        response = self.client.post(
            "/api/user/get_verification",
            data={"email": "test@email.testemail"},
            content_type="multipart/form-data",
        )

        verification_code = test_redis.get("vcode#test@email.testemail")
        self.assertIsNotNone(verification_code)
        verification_code = verification_code.decode("utf-8")
        self.assertTrue(len(verification_code) > 0)

        with mail.record_messages() as outbox:
            response = self.client.post(
                "/api/user/register",
                data={
                    "email": "test@email.testemail",
                    "nickname": "test",
                    "password": "test_password",
                    "verification_code": verification_code,
                },
                content_type="multipart/form-data",
            )
            self.assertEqual(len(outbox), 1)

        payload = self.check_success_field(response)
        self.assertEqual(payload["code"], 310)

        user_id = payload["data"]["id"]
        token = payload["data"]["token"]
        user = User.get_by_id(user_id)
        self.assertIsNotNone(user)
        self.assertTrue(user.verify_token(token)[0])

    def test_api_change_email(self):
        self.register()

        user = User.get_by_email("test@email.testemail")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@email.testemail")

        response = self.client.post(
            "/api/user/change_email",
            data={
                "email": "test@email.testemail",
                "new_email": "test_new@email.testemail",
            },
            content_type="multipart/form-data",
        )
        self.check_success_field(response)

        user = User.get_by_email("test@email.testemail")
        self.assertIsNone(user)
        user = User.get_by_email("test_new@email.testemail")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test_new@email.testemail")

    def test_api_change_password(self):
        self.register()

        self.assertTrue(User.login_check("test@email.testemail", "test_password"))

        response = self.client.post(
            "/api/user/change_password",
            data={
                "email": "test@email.testemail",
                "password": "test_password",
                "new_password": "test_new_password",
            },
            content_type="multipart/form-data",
        )
        payload = self.check_success_field(response)
        self.assertEqual(payload["code"], 0)

        self.assertFalse(User.login_check("test@email.testemail", "test_password"))
        self.assertTrue(User.login_check("test@email.testemail", "test_new_password"))

    def test_api_get_user_info(self):
        self.register()
        response = self.client.post(
            "/api/user/info",
            data={"email": "test@email.testemail"},
            content_type="multipart/form-data",
        )
        payload = self.check_success_field(response)
        self.assertEqual(payload["code"], 0)

        user_info = payload["data"]
        self.assertEqual(user_info["email"], "test@email.testemail")
        self.assertEqual(user_info["nickname"], "test")
        self.assertEqual(user_info["role"], User.Role.mapping.get(User.Role.USER))

        # TODO: test info for researcher
