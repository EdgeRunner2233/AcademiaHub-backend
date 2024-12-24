import io
import unittest
from src import create_app
import src.config as config
import tests.util as test_util
from fakeredis import FakeRedis
from unittest.mock import patch
from src.extensions import db, mail
from werkzeug.datastructures import FileStorage


class FakeObs:
    files: dict[str, bytes] = dict()

    class ObsOperationError(Exception):
        """
        An error class for OBS
        """

    def __init__(self):
        pass

    def put_file(
        self, content: bytes, obs_filename: str, obs_dir=config.OBS_AVATAR_PREFIX
    ) -> str:
        self.files[obs_dir + obs_filename] = content
        return config.OBS_BASE_URL + obs_dir + obs_filename

    def delete_file(self, obs_filename: str, obs_dir=config.OBS_AVATAR_PREFIX) -> bool:
        self.files.pop(obs_dir + obs_filename)
        return True


test_redis = FakeRedis()
fake_obs = FakeObs()


@patch("src.cache.redis", test_redis)
@patch("src.service.user.obs_client", fake_obs)
class AdminApiTestCase(unittest.TestCase):
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

    def request_become_researcher(self, user_id=1):
        response = self.client.post(
            "/api/user/become_researcher",
            data={
                "user_id": user_id,
                "researcher_id": "A5067514564",
                "name": "Tim Dettmers",
                "gender": "男",
                "birth_date": "2000-01-01",
                "phone_number": "123321123",
                "email": "non@non.existent",
                "address": "address",
                "academic": "大学本科",
                "graduated_school": "graduated_school",
                "certificate": FileStorage(io.BytesIO(b"Testing"), "test.txt"),
                "img1": FileStorage(io.BytesIO(b"Testing"), "test.txt"),
                "img2": FileStorage(io.BytesIO(b"Testing"), "test.txt"),
                "achievement": FileStorage(io.BytesIO(b"Testing"), "test.txt"),
                "avatar": FileStorage(io.BytesIO(b"Testing"), "test.txt"),
            },
            content_type="multipart/form-data",
        )
        return response

    def test_get_researcher_applications(self):
        self.register()

        response = self.client.post(
            "/api/admin/get_researcher_applications",
            data={"user_id": "1"},
            content_type="multipart/form-data",
        )

        payload = test_util.check_success_field(response)
        data = payload["data"]
        self.assertIn("applications", data)
        self.assertIsInstance(data["applications"], list)

    def test_feedback(self):
        # get unread feedbacks
        response = self.client.post(
            "/api/admin/get_unread_feedback",
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        data = payload["data"]
        self.assertIn("feedbacks", data)
        self.assertIsInstance(data["feedbacks"], list)
        self.assertEqual(len(data["feedbacks"]), 0)

        # feedback missing work
        self.register()
        response = self.client.post(
            "/api/user/feedback_missing_work",
            data={"content": "test"},
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)

        # get unread feedback
        response = self.client.post(
            "/api/admin/get_unread_feedback",
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        data = payload["data"]
        self.assertIn("feedbacks", data)
        self.assertIsInstance(data["feedbacks"], list)
        self.assertEqual(len(data["feedbacks"]), 1)
        self.assertEqual(data["feedbacks"][0]["content"], "test")

        # read feedback
        response = self.client.post(
            "/api/admin/read_feedback",
            data={"id": 1},
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)

        # get unread feedback
        response = self.client.post(
            "/api/admin/get_unread_feedback",
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        data = payload["data"]
        self.assertIn("feedbacks", data)
        self.assertIsInstance(data["feedbacks"], list)
        self.assertEqual(len(data["feedbacks"]), 0)

    def test_get_user_num(self):
        response = self.client.post(
            "/api/admin/user_num",
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)
        data = payload["data"]
        self.assertIn("user_num", data)
        self.assertIn("researcher_num", data)
        self.assertEqual(data["user_num"], 0)
        self.assertEqual(data["researcher_num"], 0)

        self.register()

        response = self.client.post(
            "/api/admin/user_num",
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)
        data = payload["data"]
        self.assertIn("user_num", data)
        self.assertIn("researcher_num", data)
        self.assertEqual(data["user_num"], 1)
        self.assertEqual(data["researcher_num"], 0)

    def test_researcher_application(self):
        self.register()

        # get user num
        response = self.client.post(
            "/api/admin/user_num",
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)
        data = payload["data"]
        self.assertIn("user_num", data)
        self.assertIn("researcher_num", data)
        self.assertEqual(data["user_num"], 1)
        self.assertEqual(data["researcher_num"], 0)

        # get researcher applications
        response = self.client.post(
            "/api/admin/get_researcher_applications",
            data={"user_id": "1"},
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)
        data = payload["data"]
        self.assertIn("applications", data)
        apps = data["applications"]
        self.assertIsInstance(apps, list)
        self.assertEqual(len(apps), 0)

        # approve application
        with mail.record_messages() as outbox:
            self.assertEqual(len(outbox), 0)
            response = self.client.post(
                "/api/admin/approve_researcher_application",
                data={"id": "1", "user_id": "1"},
                content_type="multipart/form-data",
            )
            self.assertEqual(len(outbox), 0)
        payload = test_util.check_fail_field(response)
        self.assertEqual(payload["code"], 511)

        # disapprove application
        response = self.client.post(
            "/api/admin/disapprove_researcher_application",
            data={"id": "1", "user_id": "1"},
            content_type="multipart/form-data",
        )
        payload = test_util.check_fail_field(response)
        self.assertEqual(payload["code"], 511)

        # become researcher
        response = self.request_become_researcher()
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 510)

        # duplicate become researcher request
        response = self.request_become_researcher()
        payload = test_util.check_fail_field(response)
        self.assertEqual(payload["code"], 507)

        # get researcher applications
        response = self.client.post(
            "/api/admin/get_researcher_applications",
            data={"user_id": "1"},
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)
        data = payload["data"]
        self.assertIn("applications", data)
        apps = data["applications"]
        self.assertIsInstance(apps, list)
        self.assertEqual(len(apps), 1)
        self.assertIn("user_id", apps[0])
        self.assertEqual(apps[0]["user_id"], 1)

        # approve application
        with mail.record_messages() as outbox:
            self.assertEqual(len(outbox), 0)
            response = self.client.post(
                "/api/admin/approve_researcher_application",
                data={"id": "1", "user_id": "1"},
                content_type="multipart/form-data",
            )
            self.assertEqual(len(outbox), 1)
            self.assertEqual(len(outbox[0].recipients), 1)
            self.assertEqual(outbox[0].recipients[0], "test@email.testemail")
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)

        # duplicate approve application
        with mail.record_messages() as outbox:
            self.assertEqual(len(outbox), 0)
            response = self.client.post(
                "/api/admin/approve_researcher_application",
                data={"id": "1", "user_id": "1"},
                content_type="multipart/form-data",
            )
            self.assertEqual(len(outbox), 0)
        payload = test_util.check_fail_field(response)
        self.assertEqual(payload["code"], 511)

        # disapprove application
        response = self.client.post(
            "/api/admin/disapprove_researcher_application",
            data={"id": "1", "user_id": "1"},
            content_type="multipart/form-data",
        )
        payload = test_util.check_fail_field(response)
        self.assertEqual(payload["code"], 511)

        # get no researcher applications after approving
        response = self.client.post(
            "/api/admin/get_researcher_applications",
            data={"user_id": "1"},
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)
        data = payload["data"]
        self.assertIn("applications", data)
        apps = data["applications"]
        self.assertIsInstance(apps, list)
        self.assertEqual(len(apps), 0)

        # get user num
        response = self.client.post(
            "/api/admin/user_num",
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)
        data = payload["data"]
        self.assertIn("user_num", data)
        self.assertIn("researcher_num", data)
        self.assertEqual(data["user_num"], 0)
        self.assertEqual(data["researcher_num"], 1)

        # register another user and request to become researcher
        self.register("test2@email.testemail", "test2", "test_password2")
        response = self.request_become_researcher(2)
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 510)

        # get user num
        response = self.client.post(
            "/api/admin/user_num",
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)
        data = payload["data"]
        self.assertIn("user_num", data)
        self.assertIn("researcher_num", data)
        self.assertEqual(data["user_num"], 1)
        self.assertEqual(data["researcher_num"], 1)

        # disapprove application
        response = self.client.post(
            "/api/admin/disapprove_researcher_application",
            data={"id": "1", "user_id": "2"},
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)

        # get no researcher applications after disapproving
        response = self.client.post(
            "/api/admin/get_researcher_applications",
            data={"user_id": "1"},
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)
        data = payload["data"]
        self.assertIn("applications", data)
        apps = data["applications"]
        self.assertIsInstance(apps, list)
        self.assertEqual(len(apps), 0)

        # get user num
        response = self.client.post(
            "/api/admin/user_num",
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)
        data = payload["data"]
        self.assertIn("user_num", data)
        self.assertIn("researcher_num", data)
        self.assertEqual(data["user_num"], 1)
        self.assertEqual(data["researcher_num"], 1)

        # request to become researcher again
        response = self.request_become_researcher(2)
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 510)

        # approve application
        with mail.record_messages() as outbox:
            self.assertEqual(len(outbox), 0)
            response = self.client.post(
                "/api/admin/approve_researcher_application",
                data={"id": "1", "user_id": "2"},
                content_type="multipart/form-data",
            )
            self.assertEqual(len(outbox), 1)
            self.assertEqual(len(outbox[0].recipients), 1)
            self.assertEqual(outbox[0].recipients[0], "test2@email.testemail")
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)

        # get no researcher applications after approving
        response = self.client.post(
            "/api/admin/get_researcher_applications",
            data={"user_id": "1"},
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)
        data = payload["data"]
        self.assertIn("applications", data)
        apps = data["applications"]
        self.assertIsInstance(apps, list)
        self.assertEqual(len(apps), 0)

        # get user num
        response = self.client.post(
            "/api/admin/user_num",
            content_type="multipart/form-data",
        )
        payload = test_util.check_success_field(response)
        self.assertEqual(payload["code"], 0)
        data = payload["data"]
        self.assertIn("user_num", data)
        self.assertIn("researcher_num", data)
        self.assertEqual(data["user_num"], 0)
        self.assertEqual(data["researcher_num"], 2)
