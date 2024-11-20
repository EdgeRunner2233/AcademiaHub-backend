import unittest
from src.model import User
from src import create_app
from src.extensions import db


class DatabaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
        cls.test_db = db
        cls.app_context = cls.app.app_context()

    def setUp(self):
        self.app_context.push()

        self.test_db.create_all()
        user_1 = User(id=1, name="test_1")
        user_2 = User(id=2, name="test_2")
        self.test_db.session.add_all([user_1, user_2])
        self.test_db.session.commit()

    def tearDown(self):
        self.test_db.session.remove()
        self.test_db.drop_all()

        self.app_context.pop()

    def test_app_exist(self):
        self.assertIsNotNone(self.app)

    def test_app_is_testing(self):
        self.assertTrue(self.app.testing)
        self.assertTrue(self.app.config["TESTING"])

    def test_query_first(self):
        user = User.query_first(id=1)
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "test_1")

    def test_query_all(self):
        users = User.query_all()
        self.assertEqual(len(users), 2)

    def test_save(self):
        user = User.query_first(id=3)
        self.assertIsNone(user)

        user = User(id=3, name="test_3")
        self.assertTrue(user.save())

        user = User.query_first(id=3)
        self.assertIsNotNone(user)

    def test_delete(self):
        user = User.query_first(id=1)
        self.assertIsNotNone(user)
        self.assertTrue(user.delete())

        user = User.query_first(id=1)
        self.assertIsNone(user)

        user = User.query_first(id=1, is_deleted=True)
        self.assertIsNotNone(user)

    def test_delete_force(self):
        user = User.query_first(id=1)
        self.assertIsNotNone(user)
        self.assertTrue(user.delete(force=True))

        user = User.query_first(id=1)
        self.assertIsNone(user)

        user = User.query_first(id=1, is_deleted=True)
        self.assertIsNone(user)

    def test_update(self):
        user = User.query_first(id=1)
        self.assertIsNotNone(user)
        self.assertTrue(user.update(name="test_1_update"))

        user = User.query_first(id=1)
        self.assertEqual(user.name, "test_1_update")
