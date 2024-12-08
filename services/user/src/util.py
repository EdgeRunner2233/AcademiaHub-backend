import os
import re
import random
from authlib.jose import jwt
from src.extensions import mail, redis
from flask_mail import Message as MailMessage
from authlib.jose.errors import BadSignatureError
from datetime import datetime, timedelta, timezone


def get_logger():
    _logger = None

    def _get_singleton():
        nonlocal _logger
        if _logger is None:
            import logging
            import logging.config
            from pathlib import Path

            ini_path = Path(__file__).absolute().parent.parent / "logging.ini"
            logging.config.fileConfig(ini_path.as_posix())
            _logger = logging.getLogger("infoLogger")
        return _logger

    return _get_singleton()


logger = get_logger()


class Token:
    header = {"alg": "HS256", "typ": "JWT"}
    secret = os.getenv("TOKEN_SECRET", "dev")
    expire_time = int(os.getenv("TOKEN_EXPIRE_TIME", 3600))

    class TokenExpired(Exception):
        pass

    class TokenInvalid(Exception):
        pass

    @staticmethod
    def generate_token(payload: dict = {}) -> str:
        """
        Generate a token with given payload.

        Args:
            payload (dict): Payload to be encoded.

        Returns:
            str: Encoded token.
        """

        expiration_time = datetime.now(timezone.utc) + timedelta(
            seconds=float(Token.expire_time)
        )
        payload.update({"exp": expiration_time})
        return jwt.encode(Token.header, payload, Token.secret).decode("utf-8")

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verify a token and return its payload.

        Args:
            token (str): Token to be verified.

        Raises:
            TokenExpired: If token is expired.
            TokenInvalid: If token is invalid.

        Returns:
            dict: Decoded payload.
        """

        try:
            claims = jwt.decode(token, Token.secret)
        except BadSignatureError:
            raise Token.TokenInvalid
        if claims.get("exp") < int(datetime.now(timezone.utc).timestamp()):
            raise Token.TokenExpired

        return dict(claims)


def check_email_pattern(email: str) -> bool:
    """
    Check if email is valid.

    Args:
        email (str): Email to be checked.

    Returns:
        bool: True if email is valid, False otherwise.
    """

    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


class EmailMessage:
    @staticmethod
    def _send(subject: str, recipients: str, body: str):
        message = MailMessage(subject, [recipients], body)
        mail.send(message)

    @staticmethod
    def generate_vcode() -> str:
        """
        Generate a 6-digit verification code.

        Returns:
            str: verification code.
        """

        code = "".join([str(int(random.random() * 10)) for _ in range(6)])
        return code

    @staticmethod
    def send_vcode(email: str) -> None:
        """
        Generate and send verification code to user.

        Args:
            email (str): user email.

        Returns:
            None
        """

        subject = "[AcademiaHub] 验证码: {code}"
        body = (
            "感谢您注册AcademiaHub, 您的验证码为: {code}, 10分钟内有效。\n\n"
            + "Thank you for registering on AcademiaHub. "
            + "Your verification code is: {code}, valid for 10 minutes.\n\n\n"
            + "----------\nAcademiaHub Team"
        )

        def _construct_subject_body(code: str) -> tuple[str, str]:
            return (
                subject.format(code=code),
                body.format(code=code),
            )

        code = EmailMessage.generate_vcode()

        redis.set(email, code, ex=600)

        subject_body = _construct_subject_body(code)

        EmailMessage._send(subject_body[0], email, subject_body[1])

    @staticmethod
    def send_register_success(email: str) -> None:
        """
        Send register success message to user.

        Args:
            email (str): user email.

        Returns:
            None
        """

        subject = "[AcademiaHub] 感谢您注册!"
        body = (
            "您的邮箱账户已激活。感谢您注册AcademiaHub! \n\n"
            + "Your email has been activated. Thank you for registering on AcademiaHub! \n\n\n"
            + "----------\nAcademiaHub Team"
        )

        EmailMessage._send(subject, email, body)

    @staticmethod
    def verify_vcode(email: str, code: str) -> bool:
        """
        Verify verification code.

        Args:
            email (str): user email.
            code (str): verification code.

        Returns:
            bool: True if verification code is correct, False otherwise.
        """

        valid_code = redis.get(email)
        valid_code = valid_code.decode("utf-8") if valid_code is not None else None  # type: ignore
        if valid_code and valid_code == code:
            redis.delete(email)
            return True
        else:
            return False
