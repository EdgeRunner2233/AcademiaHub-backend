import json

from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

from utils.search_utils import *
from .models import *
from .tasks import *
from history.models import *
import threading
import logging
import requests
from .tasks import *
import re
logger = logging.getLogger('mylogger')


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
        inside_operand = False
        operand = ""

        while i < len(self.expression):
            ch = self.expression[i]

            if ch.isspace():
                if inside_operand:
                    operand += ch  # 将空格加入当前操作数
                i += 1
                continue

            if ch.isalnum():
                if not inside_operand:
                    inside_operand = True
                    operand = ch
                else:
                    operand += ch
            else:
                if inside_operand:
                    output.append(operand.strip())
                    inside_operand = False

                if ch == '(':
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

        if inside_operand:
            output.append(operand.strip())

        while operators:
            output.append(operators.pop())

        return output

    def postfix_to_infix(self, postfix):
        """将后缀表达式转换为没有括号的形式"""
        stack = []

        for token in postfix:
            if token.isalnum() or " " in token:
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
def add_search_word_num(words):
    def task():
        word = words.strip('"')
        word = word.lower()
        word_new, created = SearchWord.objects.get_or_create(
            word=word,
            defaults={'number': 1}  # 新记录时赋值
        )

        if not created:
            word_new.number += 1
            word_new.save()

    threading.Thread(target=task).start()

# def save_history(user_id, text):
#     History.

# 普通搜索
@require_POST
def ordinary_search(request):
    logger.info("ordinary_search")
    user_id = request.POST.get('user_id', '')
    text = request.POST.get('key', '')
    type = request.POST.get('type', '') # 1: 作者 0: 文献
    page = request.POST.get('page', '')
    value = openAlex_ordinary_search(text, type, page)

    # if user_id:
    #     ;

    if type == '0':
        # 将词条存入search-word
        # 启动后台任务计算统计信息
        calculate_statistics.delay({'filter':"default.search:"+text})
        add_search_word_num(text)

    result = {'type': type,'search_str':"default.search:"+text, 'result': value}

    return JsonResponse(result)


def get_top10_searches(num):
    top_searches = SearchWork.objects.all().order_by('-number')[:num]
    return [search.to_dic() for search in top_searches]

# 周热门搜索文章
@require_POST
def get_weekly_popular_works(request):
    num = request.POST.get('num', '')
    if num == '':
        num = 10
    result = {'result': get_top10_searches(int(num))}
    return JsonResponse(result)

def add_search_work_num(work_id, work_title):
    def task():
        work, created = SearchWork.objects.get_or_create(
            work_id=work_id,
            defaults={'work_title': work_title, 'number': 1}  # 新记录时赋值
        )

        if not created:
            work.number += 1
            work.save()

    threading.Thread(target=task).start()


def getIeeeJournalFormat(bibInfo):
    """
    生成期刊文献的IEEE引用格式：{作者}, "{文章标题}," {期刊名称}, vol. {卷数}, no. {编号}, pp. {页码}, {年份}.
    :return: {author}, "{title}," {journal}, vol. {volume}, no. {number}, pp. {pages}, {year}.
    """
    # 避免字典出现null值
    if "volume" not in bibInfo:
        bibInfo["volume"] = "null"
    if "number" not in bibInfo:
        bibInfo["number"] = "null"
    if "pages" not in bibInfo:
        bibInfo["pages"] = "null"

    journalFormat =  bibInfo["author"] + \
           ", \"" + bibInfo["title"] + \
           ",\" " + bibInfo["journal"] + \
           ", vol. " + bibInfo["volume"] + \
           ", no. " + bibInfo["number"] + \
           ", pp. " + bibInfo["pages"] + \
           ", " + bibInfo["year"] + "."

    # 对格式进行调整，去掉没有的信息，调整页码格式
    journalFormatNormal = journalFormat.replace(", vol. null", "")
    journalFormatNormal = journalFormatNormal.replace(", no. null", "")
    journalFormatNormal = journalFormatNormal.replace(", pp. null", "")
    journalFormatNormal = journalFormatNormal.replace("--", "-")
    return journalFormatNormal

def getIeeeConferenceFormat(bibInfo):
    """
    生成会议文献的IEEE引用格式：{作者}, "{文章标题}, " in {会议名称}, {年份}, pp. {页码}.
    :return: {author}, "{title}, " in {booktitle}, {year}, pp. {pages}.
    """
    conferenceFormat = bibInfo["author"] + \
                    ", \"" + bibInfo["title"] + ",\" " + \
                    ", in " + bibInfo["booktitle"] + \
                    ", " + bibInfo["year"] + \
                    ", pp. " + bibInfo["pages"] + "."

    # 对格式进行调整，，调整页码格式
    conferenceFormatNormal = conferenceFormat.replace("--", "-")
    return conferenceFormatNormal

def getIeeeFormat(bibInfo):
    """
    本函数用于根据文献类型调用相应函数来输出ieee文献引用格式
    :param bibInfo: 提取出的BibTeX引用信息
    :return: ieee引用格式
    """
    if "journal" in bibInfo: # 期刊论文
        return getIeeeJournalFormat(bibInfo)
    elif "booktitle" in bibInfo: # 会议论文
        return getIeeeConferenceFormat(bibInfo)

def inforDir(bibtex):
    #pattern = "[\w]+={[^{}]+}"   用正则表达式匹配符合 ...={...} 的字符串
    pattern1 = "[\w]+=" # 用正则表达式匹配符合 ...= 的字符串
    pattern2 = "{[^{}]+}" # 用正则表达式匹配符合 内层{...} 的字符串

    # 找到所有的...=，并去除=号
    result1 = re.findall(pattern1, bibtex)
    for index in range(len(result1)) :
        result1[index] = re.sub('=', '', result1[index])
    # 找到所有的{...}，并去除{和}号
    result2 = re.findall(pattern2, bibtex)
    for index in range(len(result2)) :
        result2[index] = re.sub('\{', '', result2[index])
        result2[index] = re.sub('\}', '', result2[index])

    # 创建BibTeX引用字典，归档所有有效信息
    infordir = {}
    for index in range(len(result1)):
        infordir[result1[index]] = result2[index]
    return infordir

def generate_bibtex(specific_work):
    """
    根据获取到的特定工作生成 BibTeX 格式的引用。
    :param specific_work: 获取到的特定工作数据
    :return: BibTeX 格式的引用字符串
    """
    # 从 specific_work 中提取数据
    authorships = specific_work.get("authorships", [])
    title = specific_work.get("title", "")
    year = specific_work.get("publication_year", "")
    pages = specific_work.get("pages", "")
    volume = specific_work.get("volume", "")
    number = specific_work.get("number", "")
    flag =0  # flag: 0-journal

    if specific_work.get("primary_location","").get("source").get("type","") == "journal":
        flag = 0
        journal = specific_work.get("primary_location","").get("source").get("display_name","")
    elif specific_work.get("primary_location","").get("source").get("type","") == "conference":
        flag = 1
        booktitle = specific_work.get("primary_location","").get("source").get("display_name","")
    else:
        flag = 2

    # 从 authorships 提取作者的 display_name
    author_names = [authorship.get("author", {}).get("display_name", "") for authorship in authorships]
    author_str = " and ".join(author_names)


    # 选择生成期刊论文或会议论文
    if flag == 0:  # 如果有期刊
        bibtex = f"@article{{{specific_work['id']},\n"
        bibtex += f"author={{{author_str}}},\n"
        bibtex += f"title={{{title}}},\n"
        bibtex += f"journal= {{{journal}}},\n"
        if volume:
            bibtex += f"volume={{{volume}}},\n"
        if number:
            bibtex += f"number={{{number}}},\n"
        if pages:
            bibtex += f"pages={{{pages}}},\n"
        bibtex += f"year={{{year}}}\n"
        bibtex += "}"

    elif flag == 1:  # 如果是会议论文
        bibtex = f"@inproceedings{{{specific_work['id']},\n"
        bibtex += f"author={{{author_str}}},\n"
        bibtex += f"title={{{title}}},\n"
        bibtex += f"booktitle={{{booktitle}}},\n"
        if pages:
            bibtex += f"pages={{{pages}}},\n"
        bibtex += f"year={{{year}}}\n"
        bibtex += "}"

    else:
        bibtex = ""

    return bibtex


# 获得特定的文章
@require_POST
def get_specific_work(request):
    openalex_id = request.POST.get('openalex_id', '')
    specific_work = get_single_work(openalex_id)
    work_id = specific_work['id']
    work_title = specific_work['title']

    # 生成 BibTeX 引用格式
    bibtex = generate_bibtex(specific_work)

    # 转换为 IEEE 格式
    bibtex_info = inforDir(bibtex)  # 将 BibTeX 转换为字典
    ieee_format = getIeeeFormat(bibtex_info)  # 转换为 IEEE 格式

    specific_work['pdf'] = None
    for location in specific_work['locations']:
        pdf_url = location.get("pdf_url")
        if pdf_url is not None:
            specific_work['pdf'] = pdf_url
            break

    add_search_work_num(work_id, work_title)

    result = {
        'bibtex': bibtex,  # 返回 BibTeX 格式的引用
        'ieee': ieee_format,  # 返回 IEEE 格式的引用
        'result': specific_work
    }
    return JsonResponse(result)

def get_top10_words(num):
    top_words = SearchWord.objects.all().order_by('-number')[:]
    return [words.to_dic() for words in top_words]

# 周热门搜索词条
@require_POST
def get_weekly_popular_words(request):
    num = request.POST.get('num', '')
    if num == '':
        num = 10
    result = {'result': get_top10_words(int(num))}
    return JsonResponse(result)

@require_POST
def get_new_works(request):
    num = request.POST.get('num', '')
    if num == '':
        num = 10
    num = int(num)
    works_list = cache.get('new_works' + str(num))
    if works_list is None:
        works = NewWorks.objects.all().order_by('-publication_date')[:num]
        works_list = [work.to_dic() for work in works]
        cache.set('new_works' + str(num), works_list)

    return JsonResponse({'result': works_list}, safe=False)



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

                    if not author_ids:
                        return JsonResponse(
                            {"result": []},)

                    authors = '|'.join(author_ids)
                    processed_filters.append(f"author.id:{authors}")

                elif key == "topic":
                    # 处理主题过滤
                    parser = LogicExpressionParser(value)
                    topic_ids=get_topic_id(parser.parse())
                    
                    if not topic_ids:
                        return JsonResponse(
                            {"result": []},)
                    
                    topics = '|'.join(topic_ids)
                    processed_filters.append(f"topics.id:{topics}")

                else:
                    # 默认处理
                    processed_filters.append(f"{key}:{value}")

            # 构造最终的过滤字符串
            filter_string = ",".join(processed_filters)
            params = {'filter': filter_string} if filter_string else {}
            # 启动后台任务计算统计信息
            calculate_statistics.delay(params)

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
                return JsonResponse({"search_str":filter_string,"result": response.json()}, status=200, safe=False)
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

def get_statistics(request):
    query = request.POST.get('search_str', '')  # 获取搜索关键词

    # 尝试从数据库中获取统计数据
    try:
        stats = Statistics.objects.filter(filter=query).first()
        return JsonResponse({'status': 'completed', 'stats': {
            'publication_year_list': stats.publication_year_list,
            'type_list': stats.type_list,
            'author_list': stats.author_list,
        }})
    except Statistics.DoesNotExist:
        # 如果数据不存在，说明还在处理中
        return JsonResponse({'status': 'processing'})
