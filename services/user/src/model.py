import pytz
import sqlalchemy as sql
from src.util import logger
from src.cache import Token
import src.config as config
import sqlalchemy.exc as exc
from datetime import datetime
from src.extensions import db
import werkzeug.security as security
from typing import Type, TypeVar, Optional, Union, Tuple, List


T = TypeVar("T", bound="Base")
tz = pytz.timezone("Asia/Shanghai")


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
        ins = self.__class__.query_first(id=self.id)  # type: ignore
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
        return cls.query.filter_by(**filter).first()  # type: ignore

    @classmethod
    def query_all(cls: Type[T], **filter: Union[int, str, bool]) -> List[T]:
        if "is_deleted" not in filter:
            filter["is_deleted"] = False
        return cls.query.filter_by(**filter).all()  # type: ignore


class User(db.Model, Base):  # type: ignore
    class Role:
        USER = 0
        RESEARCHER = 1
        ADMIN = 2
        SUPER_ADMIN = 3

        mapping = {
            0: "user",
            1: "researcher",
            2: "admin",
            3: "super_admin",
        }

    id = sql.Column(sql.Integer, primary_key=True)
    role = sql.Column(sql.Integer, default=Role.USER)

    email = sql.Column(sql.String(50))
    nickname = sql.Column(sql.String(20))
    password_hash = sql.Column(sql.String(256))

    avatar_url = sql.Column(sql.String(150), default=config.DEFAULT_AVATAR_URL)

    gmt_registered = sql.Column(sql.DateTime, default=datetime.now(tz))
    gmt_created = sql.Column(sql.DateTime, default=datetime.now(tz))
    gmt_modified = sql.Column(sql.DateTime, default=datetime.now(tz))

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
        return security.check_password_hash(str(user.password_hash), plain_password)

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

    def info(self) -> dict:
        """
        Get the user info.

        Returns:
            dict: The user info.
        """
        user_info = {
            "id": self.id,
            "email": self.email,
            "nickname": self.nickname,
            "time_registered": self.gmt_registered.strftime("%Y-%m-%d %H:%M:%S"),
            "role": User.Role.mapping.get(int(self.role)),
        }
        if self.role == User.Role.RESEARCHER:
            researcher = Researcher.get_by_user_id(self.id)
            user_info.update(
                {
                    "is_applied_for_researcher": researcher is not None,
                    "researcher_info": researcher.info() if researcher else {},
                }
            )
        return user_info

    def __repr__(self):
        return f"<User {self.email}({self.id})>"


class ResearcherApplication(Base):
    user_id = sql.Column(sql.Integer)

    certificate = sql.Column(sql.String(200), nullable=False)
    id_card_front = sql.Column(sql.String(200), nullable=False)
    id_card_back = sql.Column(sql.String(200), nullable=False)
    academic_achievement = sql.Column(sql.String(200), nullable=False)

    gmt_created = sql.Column(sql.DateTime, default=datetime.now(tz))
    gmt_modified = sql.Column(sql.DateTime, default=datetime.now(tz))
    is_deleted = sql.Column(sql.Boolean, default=False)

    def create(
        self,
        certificate: str,
        id_card_front: str,
        id_card_back: str,
        academic_achievement: str,
    ) -> Optional["ResearcherApplication"]:
        """
        Create the application.

        Args:
            certificate (str): The certificate of the user for application.
            id_card_front (str): The front side of the ID card.
            id_card_back (str): The back side of the ID card.
            academic_achievement (str): The academic achievement of the user.

        Returns:
            bool: Whether the application is created successfully.
        """

        researcher_application = ResearcherApplication(
            certificate=certificate,
            id_card_front=id_card_front,
            id_card_back=id_card_back,
            academic_achievement=academic_achievement,
        )

        return researcher_application if researcher_application.save() else None

    def get_by_user_id(user_id: int) -> Optional["ResearcherApplication"]:
        """
        Get the application with given user_id.

        Args:
            user_id (int): The id of the user.

        Returns:
            Optional[ResearcherApplication]: The application with given user_id or None if not found.
        """

        return ResearcherApplication.query_first(user_id=user_id)


class Researcher(Base):
    user_id = sql.Column(sql.Integer, nullable=False)
    openalex_id = sql.Column(sql.String(50), nullable=False)

    real_name = sql.Column(sql.String(20), default="")
    gender = sql.Column(sql.String(10), default="")
    birth_date = sql.Column(sql.String(20), default="")
    phone_number = sql.Column(sql.String(20), default="")
    researcher_email = sql.Column(sql.String(50), default="")
    address = sql.Column(sql.String(50), default="")
    academic_background = sql.Column(sql.String(20), default="")
    graduated_from = sql.Column(sql.String(30), default="")

    is_valid = sql.Column(sql.Boolean, default=False)

    gmt_became_researcher = sql.Column(sql.DateTime, default=datetime.now(tz))
    gmt_created = sql.Column(sql.DateTime, default=datetime.now(tz))
    gmt_modified = sql.Column(sql.DateTime, default=datetime.now(tz))
    is_deleted = sql.Column(sql.Boolean, default=False)

    @staticmethod
    def create(
        user_id: int,
        openalex_id: str,
        real_name: str,
        gender: str,
        birth_date: str,
        phone_number: str,
        researcher_email: str,
        address: str,
        academic_background: str,
        graduated_from: str,
    ) -> Optional["Researcher"]:
        """
        Create a new researcher (from a user) and save it to database.

        Args:
            user_id (int): The id of the user.
            openalex_id (str): The openalex id of the user.
            real_name (str): The real name of the user.
            gender (str): The gender of the user.
            birth_date (str): The birth date of the user.
            phone_number (str): The phone number of the user.
            researcher_email (str): The email of the user.
            address (str): The address of the user.
            academic_background (str): The academic background of the user.
            graduated_from (str): The graduated from of the user.

        Returns:
            Optional[Researcher]: The created Researcher object or None if failed.
        """

        researcher = Researcher(
            user_id=user_id,
            openalex_id=openalex_id,
            real_name=real_name,
            gender=gender,
            birth_date=birth_date,
            phone_number=phone_number,
            researcher_email=researcher_email,
            address=address,
            academic_background=academic_background,
            graduated_from=graduated_from,
        )

        return researcher if researcher.save() else None

    def get_by_user_id(user_id: int) -> Optional["Researcher"]:
        """
        Get the researcher with given user_id.

        Args:
            user_id (int): The id of the user.

        Returns:
            Optional[Researcher]: The researcher with given user_id or None if not found.
        """

        return Researcher.query_first(user_id=user_id, is_valid=True)

    def info(self) -> dict:
        """
        Get the researcher info.

        Returns:
            dict: The researcher info.
        """
        researcher_info = {
            "user_id": self.user_id,
            "openalex_id": self.openalex_id,
            "real_name": self.real_name,
            "gender": self.gender,
            "birth_date": self.birth_date,
            "phone_number": self.phone_number,
            "researcher_email": self.researcher_email,
            "address": self.address,
            "academic_background": self.academic_background,
            "graduated_from": self.graduated_from,
        }
        return researcher_info

    def __repr__(self):
        return f"<Researcher {self.real_name}({self.openalex_id})>"
