import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import requests
from utils.search_utils import openAlex_ordinary_search

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


# Create your views here.
@require_POST
def ordinary_search(request):
    text = request.POST.get('key', '')
    type = request.POST.get('type', '') # 1: 作者 2: 文献
    page = request.POST.get('page', '')
    value = openAlex_ordinary_search(text, type, page)

    result = {'type': type, 'result': value}

    return JsonResponse(result)

@require_POST
def a(request):
    result = {'type': 1}
    return JsonResponse(result)


def advanced_search(request):
    if request.method == 'POST':
        try:
            # 解析请求体
            request_body_json = json.loads(request.body.decode())

            # 构建 API 请求 URL
            base_url = "https://api.openalex.org/works"

            # 获取筛选字段
            filters = request_body_json.get('filter', {})

            # 构造过滤参数
            processed_filters = []
            for key, value in filters.items():
                if not value:  # 忽略空值
                    continue

                # 针对每个键值对的特殊处理
                if key == "abstract":
                    parser =LogicExpressionParser(value)
                    processed_filters.append(f"abstract.search:{parser.parse()}")
                elif key == "fulltext":
                    parser = LogicExpressionParser(value)
                    processed_filters.append(f"fulltext.search:{parser.parse()}")
                elif key == "raw_affiliation_strings":
                    parser = LogicExpressionParser(value)
                    processed_filters.append(f"raw_affiliation_strings.search:{parser.parse()}")
                elif key == "title":
                    parser = LogicExpressionParser(value)
                    processed_filters.append(f"title.search:{parser.parse()}")

                elif key == "publication_year":
                    parser = LogicExpressionParser(value)
                    processed_filters.append(f"publication_year:{parser.parse()}")
                elif key == "publication_date":
                    # 如果是日期范围，转成 "from:to" 格式
                    if isinstance(value, dict):
                        if 'from' in value:
                            processed_filters.append(f"from_publication_date:{value['from']}")
                        if 'to' in value:
                            processed_filters.append(f"to_publication_date:{value['to']}")
                    else:
                        processed_filters.append(f"{key}:{value}")

                elif key == "author":
                    # 处理作者过滤，例如多个作者的 OR 关系
                    parser = LogicExpressionParser(value)
                    author_ids=get_author_id(parser.parse())
                    authors = '|'.join(author_ids)
                    processed_filters.append(f"author.id:{authors}")
                elif key == "topic":
                    # 处理主题过滤
                    parser = LogicExpressionParser(value)
                    topic_ids=get_topic_id(parser.parse())
                    topics = '|'.join(topic_ids)
                    processed_filters.append(f"topics.id:{topics}")

                else:
                    # 默认处理
                    processed_filters.append(f"{key}:{value}")

            # 构造最终的过滤字符串
            filter_string = ",".join(processed_filters)
            params = {'filter': filter_string} if filter_string else {}

            # 添加分页和排序参数
            params['per-page'] = request_body_json.get('per-page', 25)
            params['page'] = request_body_json.get('page', 1)
            if 'sort' in request_body_json:
                sort_string_list = []
                sort_dict = request_body_json.get('sort', {})
                for key, value in sort_dict.items():
                    sort_string_list.append(key + ":" + value)
                sort_string = ",".join(sort_string_list)
                params['sort'] = sort_string

            # 向 OpenAlex API 发送请求
            response = requests.get(base_url, params=params)

            # 转发 API 响应
            if response.status_code == 200:
                return JsonResponse(response.json(), status=200, safe=False)
            else:
                return JsonResponse({"error": "Failed to fetch data from OpenAlex API", "details": response.json()},
                                    status=response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
        except KeyError as e:
            return JsonResponse({"error": f"Missing required key: {e}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

def get_author_id(author_name):
    """
    调用 OpenAlex authors 接口获取作者的 ID。
    """
    author_base_url = "https://api.openalex.org/authors"
    author_id_list = []
    try:
        response = requests.get(author_base_url, params={"filter": f"display_name.search:{author_name}"})
        if response.status_code == 200:
            authors = response.json().get('results', [])
            for author in authors:
                author_id_list.append(author['id'].split('/')[-1])
            return author_id_list
        return []
    except Exception as e:
        print(f"Error fetching author ID: {e}")
        return None

def get_topic_id(str):
    """
    调用 OpenAlex authors 接口获取作者的 ID。
    """
    base_url = "https://api.openalex.org/topics"
    id_list = []
    try:
        response = requests.get(base_url, params={"filter": f"display_name.search:{str}"})
        if response.status_code == 200:
            results = response.json().get('results', [])
            for result in results:
                id_list.append(result['id'].split('/')[-1])
            return id_list
        return []
    except Exception as e:
        print(f"Error fetching author ID: {e}")
        return None

def get_publisher_id(str):
    """
    调用 OpenAlex authors 接口获取作者的 ID。
    """
    base_url = "https://api.openalex.org/publishers"
    id_list = []
    try:
        response = requests.get(base_url, params={"filter": f"display_name.search:{str}"})
        if response.status_code == 200:
            results = response.json().get('results', [])
            for result in results:
                id_list.append(result['id'].split('/')[-1])
            return id_list
        return []
    except Exception as e:
        print(f"Error fetching author ID: {e}")
        return None