import unittest
from src import create_app
from src.extensions import db
import tests.util as test_util
from fakeredis import FakeRedis
from unittest.mock import patch


test_redis = FakeRedis()


@patch("src.cache.redis", test_redis)
class ResearcherApiTestCase(unittest.TestCase):
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

    def test_get_researcher_info_success(self):
        response = self.client.post(
            "/api/researcher/info",
            data={"researcher_id": "A5023888391"},
            content_type="multipart/form-data",
        )

        payload = test_util.check_success_field(response)
        data = payload["data"]

        self.assertIn("openalex_id", data)
        self.assertIn("orcid", data)
        self.assertIn("name", data)
        self.assertIn("works_count", data)
        self.assertIn("cited_by_count", data)
        self.assertIn("summary_stats", data)

    def test_get_researcher_info_fail(self):
        response = self.client.post(
            "/api/researcher/info",
            data={"researcher_id": "NON_EXIST_ID"},
            content_type="multipart/form-data",
        )

        payload = test_util.check_fail_field(response)
        self.assertEqual(payload["code"], 501)
