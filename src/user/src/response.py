from typing import Optional
from flask_babel import gettext
from dataclasses import dataclass, field


class Message:
    _mapping = {
        0: gettext("操作成功"),
        101: gettext("参数 {} 无效"),
    }

    @staticmethod
    def get(code: int, param: Optional[str] = None) -> str:
        message = Message._mapping.get(code, gettext("未知错误类型"))
        return message.format(param) if param else message


@dataclass
class Response:
    success: bool = True
    code: int = 0
    message: str = Message.get(0)
    data: object = field(default_factory=lambda: {})
    status_code: int = 200

    def to_dict(self):
        return {
            "success": self.success,
            "code": self.code,
            "message": self.message,
            "data": self.data,
        }

    def __call__(self):
        return self.to_dict(), self.status_code
