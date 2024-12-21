from django.test import TestCase

# Create your tests here.
class LogicExpressionParser:
    def __init__(self, expression):
        self.expression = expression

    def precedence(self, op):
        """定义操作符优先级"""
        if op == '!':
            return 3
        if op == '&':
            return 2
        if op == '|':
            return 1
        return 0

    def apply_operator(self, op, b, a=None):
        """应用操作符到操作数"""
        if op == '!':
            return f"!{b}"
        if op == '&':
            return f"{a}+{b}"
        if op == '|':
            return f"{a}|{b}"

    def to_postfix(self):
        """将表达式转化为后缀表达式"""
        output = []
        operators = []
        i = 0
        while i < len(self.expression):
            ch = self.expression[i]

            if ch.isspace():
                i += 1
                continue

            if ch.isalnum():
                operand = ch
                while i + 1 < len(self.expression) and self.expression[i + 1].isalnum():
                    i += 1
                    operand += self.expression[i]
                output.append(operand)
            elif ch == '(':
                operators.append(ch)
            elif ch == ')':
                while operators and operators[-1] != '(':
                    output.append(operators.pop())
                operators.pop()
            elif ch in '!&|':
                while (operators and operators[-1] != '(' and
                       self.precedence(operators[-1]) >= self.precedence(ch)):
                    output.append(operators.pop())
                operators.append(ch)
            i += 1

        while operators:
            output.append(operators.pop())

        return output

    def postfix_to_infix(self, postfix):
        """将后缀表达式转换为没有括号的形式"""
        stack = []

        for token in postfix:
            if token.isalnum():
                stack.append(token)
            elif token == '!':
                operand = stack.pop()
                stack.append(self.apply_operator(token, operand))
            elif token in '&|':
                b = stack.pop()
                a = stack.pop()
                stack.append(self.apply_operator(token, b, a))

        return stack[0]

    def parse(self):
        """解析表达式，去掉括号并替换 & 为 +"""
        postfix = self.to_postfix()
        return self.postfix_to_infix(postfix)


# 示例用法
expression = ""
parser = LogicExpressionParser(expression)
result = parser.parse()
print("输入表达式:", expression)
print("输出表达式:", result)
