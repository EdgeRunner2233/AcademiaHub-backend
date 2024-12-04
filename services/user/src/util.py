import os
import re
import random
from typing import Optional
from authlib.jose import jwt
from src.extensions import mail
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
    secret = os.getenv("TOKEN_SECRET")
    expire_time = os.getenv("TOKEN_EXPIRE_TIME")

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
            seconds=Token.expire_time
        )
        payload.update({"exp": expiration_time})
        return jwt.encode(Token.header, payload, Token.secret).decode("utf-8")

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verify a token and return its payload.

        Args:
            token (str): Token to be verified.

        Raises:
            TokenExpired: If token is expired.
            TokenInvalid: If token is invalid.

        Returns:
            Optional[dict]: Decoded payload or None if token is invalid.
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


class VerificationCode:
    subject = "[AcademiaHub] 验证码: {code}"
    body = """感谢您注册AcademiaHub, 您的验证码为: {code}。

Thank you for registering on AcademiaHub. Your verification code is: {code}.



----------

AcademiaHub Team"""

    @staticmethod
    def send(subject: str, recipients: str, body: str):
        message = MailMessage(subject, [recipients], body)
        mail.send(message)

    @staticmethod
    def generate_code() -> str:
        """
        Generate a 6-digit verification code.

        Returns:
            str: verification code.
        """

        code = "".join([str(int(random.random() * 10)) for _ in range(6)])
        return code

    @staticmethod
    def send_verification_code(email: str, code: str) -> None:
        """
        Send verification code to user.

        Args:
            email (str): user email.
            code (str): verification code.

        Returns:
            None
        """

        def construct_subject_body(code: str) -> str:
            return (
                VerificationCode.subject.format(code=code),
                VerificationCode.body.format(code=code),
            )

        subject_body = construct_subject_body(code)

        VerificationCode.send(subject_body[0], email, subject_body[1])
