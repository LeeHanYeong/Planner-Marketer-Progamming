import os
import pickle
from typing import NamedTuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

SHOW_LOG = True
CATEGORY_LEVEL_TOP = 'top'
CATEGORY_LEVEL_SUB = 'sub'
CATEGORY_LEVEL_ALL = 'all'


class Category(NamedTuple):
    pk: int
    index: int
    title: str
    url: str
    sub_categories: list


class SubCategory(NamedTuple):
    category: Category
    index: int
    pk: int
    title: str
    url: str


def log(msg):
    if SHOW_LOG:
        print(msg)


def get_categories(ask=True, refresh=False):
    try:
        if os.path.isfile('categories.pickle') and not refresh:
            categories = pickle.load(open('categories.pickle', 'rb'))
            log(f'저장된 카테고리 사용')
            return categories
    except TypeError:
        log(f'저장된 카테고리 정보가 올바르지 않아 다시 정보를 가져옵니다')

    url = 'https://kmong.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    categories = []
    for index, item in enumerate(soup.select('div.category-wrapper > .category-item')):
        if item.select_one('a'):
            url = item.select_one('a')['href']
            pk = urlparse(url).path.split('/')[-1]
            title = item.get_text(strip=True)
            category = Category(
                index=index + 1,
                pk=pk,
                title=title,
                url=url,
                sub_categories=[],
            )
            response_category = requests.get(category.url)
            soup_category = BeautifulSoup(response_category.content, 'lxml')
            for sub_index, sub_item in enumerate(
                    soup_category.select('li.category-list-item.sub-category')):
                url_sub = sub_item.select_one('a')['href']
                pk_sub = urlparse(url_sub).path.split('/')[-1]
                title_sub = sub_item.get_text(strip=True)
                sub_category = SubCategory(
                    category=category,
                    index=category.index * 10 + sub_index,
                    pk=pk_sub,
                    title=title_sub,
                    url=url_sub,
                )
                category.sub_categories.append(sub_category)
            categories.append(category)
    pickle.dump(categories, open('categories.pickle', 'wb'))
    return categories


def show_categories(categories, show_sub=False):
    for category in categories:
        print(f'{category.index:>2}: {category.title}')
        if show_sub:
            for sub_category in category.sub_categories:
                print(f' {sub_category.index:>3}: {sub_category.title}')


def main():
    categories = get_categories()
    show_categories(categories)
    # url = 'https://kmong.com/category/1'
    # response = requests.get(url)
    # soup = BeautifulSoup(response.content)
    # print(soup.prettify())


if __name__ == '__main__':
    main()
