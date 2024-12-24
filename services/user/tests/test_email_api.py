import unittest
from src import create_app
import tests.util as test_util
from fakeredis import FakeRedis
from unittest.mock import patch
from src.extensions import db, mail


test_redis = FakeRedis()


@patch("src.cache.redis", test_redis)
class UserApiTestCase(unittest.TestCase):
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

        return test_util.check_success_field(response)

    def test_send_email(self):
        with mail.record_messages() as outbox:
            self.assertEqual(len(outbox), 0)
            response = self.client.post(
                "/api/email/send",
                data={"recipient": "1", "subject": "subject", "body": "body"},
                content_type="multipart/form-data",
            )
            self.assertEqual(len(outbox), 0)
        payload = test_util.check_fail_field(response)
        self.assertEqual(payload["code"], 302)

        self.register()

        with mail.record_messages() as outbox:
            self.assertEqual(len(outbox), 0)
            response = self.client.post(
                "/api/email/send",
                data={"recipient": "1", "subject": "subject", "body": "body"},
                content_type="multipart/form-data",
            )
            self.assertEqual(len(outbox), 1)
            self.assertEqual(len(outbox[0].recipients), 1)
            self.assertEqual(outbox[0].recipients[0], "test@email.testemail")
            self.assertEqual(outbox[0].subject, "subject")
            self.assertEqual(outbox[0].body, "body")
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)
