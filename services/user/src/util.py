from typing import Optional
from authlib.jose import jwt
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
    secret = "dev"
    expire_time = 3600

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
