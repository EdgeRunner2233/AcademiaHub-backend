import json
import unittest
from src import create_app
from werkzeug.test import TestResponse

# from src.extensions import db


class ApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            MAIL_SUPPRESS_SEND=True,
        )
        # cls.test_db = db
        cls.app_context = cls.app.app_context()
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context.push()

        # self.test_db.create_all()

    def tearDown(self):
        # self.test_db.session.remove()
        # self.test_db.drop_all()

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

    def check_fail_field(self, response: TestResponse):
        self.assertEqual(response.status_code, 200)

        payload: dict = json.loads(response.data)
        self.assertIn("success", payload)
        self.assertIn("code", payload)
        self.assertIn("message", payload)
        self.assertIn("data", payload)

        if payload["success"] == True:
            print("Error: ", payload["message"])
        self.assertEqual(payload["success"], False)

        return payload

    def test_get_researcher_info_success(self):
        response = self.client.post(
            "/api/researcher/info",
            data={"researcher_id": "A5023888391"},
            content_type="multipart/form-data",
        )

        payload = self.check_success_field(response)
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

        payload = self.check_fail_field(response)
        self.assertEqual(payload["code"], 501)
