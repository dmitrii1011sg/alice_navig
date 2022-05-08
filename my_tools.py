import json
from fuzzywuzzy import fuzz

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


def find_author(author: str) -> bool:  # Проверяет, есть ли этот автор в базе данных
    if author.lower().capitalize() in [i['name'] for i in data]:
        return True
    return False


def find_poem(author: str, poem: str) -> bool:  # Проверяет, есть ли это стихотворение у этого автора
    if find_author(author):
        for current_author in data:
            if current_author['name'] == author.lower().capitalize():
                author_poems = current_author['poems']
                for current_poem in author_poems:
                    for title, content in current_poem.items():
                        if '(' in title:
                            title = title[0:title.index('(') - 1]
                        if fuzz.token_sort_ratio(poem, title.lower()) >= 60:
                            return True
                return False
    else:
        return False


def get_author(author: str) -> list:  # Возвращает список со всеми стихотворениями данного автора
    if find_author(author):
        for current_author in data:
            if current_author['name'] == author:
                return current_author['poems']
    else:
        return []


def get_poem_with_author(author: str, poem: str) -> str:  # Возвращает содержание данного стихотворения данного автора
    if find_poem(author, poem):
        for current_author in data:
            if current_author['name'] == author.lower().capitalize():
                author_poems = current_author['poems']
                for current_poem in author_poems:
                    for title, content in current_poem.items():
                        if '(' in title:
                            title = title[0:title.index('(') - 1]
                        if fuzz.token_sort_ratio(poem, title.lower()) >= 60:
                            if '____________, ' in content:
                                content = content.replace('____________, ', '')
                            if '<' in content:
                                content = ''.join(list(content)[0:list(content).index('<') - 1])
                            return content
