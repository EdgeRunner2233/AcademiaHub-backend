import sqlalchemy as sql
import sqlalchemy.exc as exc
from src.extensions import db
from src.util import logger, Token
import werkzeug.security as security
from typing import Type, TypeVar, Optional, Union, Tuple, List


T = TypeVar("T", bound="Base")


class Base:
    def save(self) -> bool:
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except exc.IntegrityError:
            logger.error(f"db: save failed: {self}")
            return False

    def delete(self, force: bool = False) -> bool:
        if not force:
            return self.update(is_deleted=True)
        else:
            logger.warning(f"db: deleting record: {self}")
            try:
                db.session.delete(self)
                db.session.commit()
                return True
            except exc.InvalidRequestError:
                logger.error(f"db: delete (force) failed: {self}")
                return False

    def update(self, **values: Union[int, str, bool]) -> bool:
        ins = self.__class__.query_first(id=self.id)
        if ins is None:
            logger.error(f"db: record not found: {self}")
            return False
        for field, value in values.items():
            if hasattr(self, field):
                setattr(self, field, value)
                setattr(ins, field, value)
            else:
                logger.error(f"db: field '{field}' not found in {self}")
        db.session.commit()
        return True

    @classmethod
    def query_first(cls: Type[T], **filter: Union[int, str, bool]) -> Optional[T]:
        if "is_deleted" not in filter:
            filter["is_deleted"] = False
        return cls.query.filter_by(**filter).first()

    @classmethod
    def query_all(cls: Type[T], **filter: Union[int, str, bool]) -> List[T]:
        if "is_deleted" not in filter:
            filter["is_deleted"] = False
        return cls.query.filter_by(**filter).all()


class User(db.Model, Base):
    class Role:
        USER = 0
        RESEARCHER = 1
        ADMIN = 2
        SUPER_ADMIN = 3

    id = sql.Column(sql.Integer, primary_key=True)
    role = sql.Column(sql.Integer, default=Role.USER)

    email = sql.Column(sql.String(50))
    nickname = sql.Column(sql.String(20))
    password_hash = sql.Column(sql.String(256))

    openalex_id = sql.Column(sql.String(30), default="")
    organization = sql.Column(sql.String(50), default="")
    title = sql.Column(sql.String(20), default="")
    research_field = sql.Column(sql.String(50), default="")
    gmt_became_researcher = sql.Column(sql.DateTime)

    gmt_registered = sql.Column(sql.DateTime, default=sql.func.now())
    gmt_created = sql.Column(sql.DateTime, default=sql.func.now())
    gmt_modified = sql.Column(sql.DateTime, default=sql.func.now())

    is_deleted = sql.Column(sql.Boolean, default=False)

    @staticmethod
    def create(email: str, nickname: str, plain_password: str) -> Optional["User"]:
        """
        Create a new user and save it to database.

        Args:
            email (str): The email of the user.
            nickname (str): The nickname of the user.
            plain_password (str): The plain text password of the user.

        Returns:
            Optional[User]: The created user object or None if failed.
        """

        user = User(
            email=email,
            nickname=nickname,
            password_hash=security.generate_password_hash(plain_password),
        )
        return user if user.save() else None

    @staticmethod
    def login_check(email: str, plain_password: str) -> bool:
        """
        Check whether the given email and password match a user in the database.

        Args:
            email (str): The email of the user.
            plain_password (str): The plain text password of the user.

        Returns:
            bool: Whether the given email and password match a user in the database.
        """

        user = User.query_first(email=email)
        if user is None:
            return False
        return security.check_password_hash(user.password_hash, plain_password)

    @staticmethod
    def exists(email: str) -> bool:
        """
        Check whether the user with given email exists in the database.

        Args:
            email (str): The email of the user.

        Returns:
            bool: Whether the given email exists in the database.
        """
        return User.query_first(email=email) is not None

    @staticmethod
    def get_by_id(id: str) -> Optional["User"]:
        """
        Get the user with given id.

        Args:
            id (str): The id of the user.

        Returns:
            Optional[User]: The user with given id or None if not found.
        """

        return User.query_first(id=id)

    @staticmethod
    def get_by_email(email: str) -> Optional["User"]:
        """
        Get the user with given email.

        Args:
            email (str): The email of the user.

        Returns:
            Optional[User]: The user with given email or None if not found.
        """

        return User.query_first(email=email)

    @staticmethod
    def generate_password_hash(plain_password: str) -> str:
        """
        Generate a password hash for the given plain text password.

        Args:
            plain_password (str): The plain text password.

        Returns:
            str: The generated password hash.
        """
        return security.generate_password_hash(plain_password)

    def generate_token(self) -> str:
        """
        Generate a token for the user.

        Returns:
            str: The generated token.
        """

        token = Token.generate_token({"id": self.id})
        return token

    @staticmethod
    def get_by_token(token: str) -> Tuple[Optional["User"], int]:
        """
        Get the user by the given token.

        Args:
            token (str): The token to get the user.

        Returns:
            tuple (Optional[User], int): A tuple of (user, error_code).
        """

        try:
            payloads = Token.verify_token(token)
        except Token.TokenExpired:
            return None, 402
        except Token.TokenInvalid:
            return None, 403

        id = payloads.get("id", None)
        user = User.query_first(id=id)
        return user, 0

    def verify_token(self, token: str) -> Tuple[bool, int]:
        """
        Verify the given token.

        Args:
            token (str): The token to verify.

        Returns:
            tuple (bool, int): A tuple of (is_valid, error_code).
        """

        try:
            payloads = Token.verify_token(token)
            if payloads.get("id") != self.id:
                return False, 403
        except Token.TokenExpired:
            return False, 402
        except Token.TokenInvalid:
            return False, 403

        return True, 0

    def __repr__(self):
        return f"<User {self.email}({self.id})>"
