import json

from diophila import OpenAlex
from django.core.cache import cache
def openAlex_ordinary_search(text, type, page):
    request_dir = {
        'text': text,
        'type': type,
        'page': page,
    }
    key = json.dumps(request_dir)
    openalex = OpenAlex()
    value = cache.get(key)
    page = int(page)
    if type is '1':
        if value is None:
            value = list(openalex.get_list_of_authors(filters=None,
                                                      search="machine learning",
                                                      sort=None,
                                                      per_page=25,
                                                      pages=[page]))

    cache.set(key, value)
    return value

