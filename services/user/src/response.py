from typing import Optional
from flask_babel import gettext
from dataclasses import dataclass, field


class Message:
    _mapping = {
        0: gettext("操作成功"),
        101: gettext("缺少参数 {}"),
        102: gettext("参数 {} 不符合格式要求"),
        300: gettext("登陆成功"),
        301: gettext("用户不存在或密码错误"),
        302: gettext("用户不存在"),
        303: gettext("请获取验证码"),
        304: gettext("验证码错误"),
        305: gettext("密码错误"),
        310: gettext("注册成功"),
        311: gettext("用户已存在"),
        319: gettext("注册失败"),
        321: gettext("用户信息更新失败: 邮箱已被占用"),
        322: gettext("用户信息更新失败: 新邮箱与原邮箱相同"),
        401: gettext("请求缺少token"),
        402: gettext("用户token已过期"),
        403: gettext("用户token无效"),
        404: gettext("无操作权限"),
        501: gettext("科研人员id不存在"),
        502: gettext("API请求失败"),
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

    def __call__(
        self, code, message_param=None, data=None, status_code=None, success=None
    ):
        self.code = code
        self.message = (
            Message.get(self.code, message_param)
            if message_param
            else Message.get(code)
        )
        if code % 10 != 0:
            self.success = False

        if data:
            self.data = data

        if status_code:
            self.status_code = status_code
        if success:
            self.success = success

        return self.to_dict(), self.status_code
