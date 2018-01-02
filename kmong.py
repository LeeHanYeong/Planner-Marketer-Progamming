import os
import pickle
from collections import OrderedDict
from typing import NamedTuple
from urllib.parse import urlparse

import requests
import xlsxwriter
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


class WorkListItem:
    WORK_TYPE_PREMIUM = 'premium'
    WORK_TYPE_PLUS = 'plus'
    WORK_TYPE_NORMAL = 'normal'
    WORK_TYPE_DICT = {
        'gig-premium-img': WORK_TYPE_PREMIUM,
        'gig-plus-img': WORK_TYPE_PLUS,
    }

    def __init__(
            self,
            pk,
            title,
            work_type,
            url_worker_profile_image,
            url_work_image,
            price,
            worker_username):
        self.pk = pk
        self.title = title
        self.work_type = work_type
        self.url_worker_profile = url_worker_profile_image
        self.url_work_image = url_work_image
        self.price = price
        self.worker_username = worker_username


def log(msg):
    if SHOW_LOG:
        print(msg)


def get_categories(ask=True, refresh=False):
    """
    크몽의 카테고리 리스트를 반환
    첫 크롤링시 categories.pickle파일을 생성해서 저장하며, 이후 저장된 파일에서 데이터를 가져옴

    :param ask:
    :param refresh: True일 경우 pickle파일을 무조건 재생성
    :return: list(Category)
    """
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


def select_category(categories):
    while True:
        show_categories(categories)
        selected = input('카테고리 선택: ')
        try:
            index = int(selected)
            for category in categories:
                if index == category.index:
                    return category
            print('오류] 해당하는 카테고리가 없습니다. 다시 선택해주세요\n')
        except Exception as e:
            print(e)


def get_works_last_page_number(category):
    """
    해당 카테고리의 pagination마지막 번호를 리턴
    :param category: 마지막 pagination번호를 가져올 카테고리
    :return:
    """
    response = requests.get(category.url)
    soup = BeautifulSoup(response.content, 'lxml')
    return int(soup.select('ul.pagination > li')[-2].get_text(strip=True))


def get_page_work_dict(category, page_number):
    """
    category의 page_number에 해당하는 작업 목록을 가져옴
    :param category: 작업 목록을 가져올 카테고리
    :param page_number: 카테고리의 pagination number
    :return: dict(WorkListItem)
    """
    params = {
        'page': page_number,
        'sort': 'created_at',
        'random': '1000',
    }
    response = requests.get(category.url, params=params)
    soup = BeautifulSoup(response.content, 'lxml')
    item_list = soup.select('#gigListContainer .gig-wrapper-default')
    work_dict = {}
    for item in item_list:
        work_type_class = item.find_next('div')['class'][0]
        pk = urlparse(item.select_one('a.plain')['href']).path.split('/')[-1]
        title = item.select_one('.gig-title').get_text(strip=True)
        url_worker_profile_image = item.select_one(
            'a > .gig-image > .gig-profile img.gig-list-user-profile')['src']
        url_work_image = item.select_one('a > .gig-image > img.width-100')['src']
        price = item.select_one('b.font-size-h4').get_text(strip=True).replace('₩', '')
        worker_username = item.select_one('.gig-username').get_text(strip=True)
        work = WorkListItem(
            pk=pk,
            title=title,
            work_type=WorkListItem.WORK_TYPE_DICT.get(
                work_type_class, WorkListItem.WORK_TYPE_NORMAL),
            url_worker_profile_image=url_worker_profile_image,
            url_work_image=url_work_image,
            price=price,
            worker_username=worker_username,
        )
        work_dict[work.pk] = work
    return work_dict


def get_work_dict(category, refresh=False, offline=False):
    pickle_name = f'work-list-items-{category.pk}.pickle'
    work_dict = {}
    try:
        if os.path.isfile(pickle_name) and not refresh:
            work_dict = pickle.load(open(pickle_name, 'rb'))
            log(f'저장된 작업 목록 사용')
            if offline:
                return work_dict
    except TypeError:
        log(f'저장된 작업 목록 정보가 올바르지 않아 다시 모든 정보를 가져옵니다')

    last_page_number = get_works_last_page_number(category)
    # for number in range(1, last_page_number + 1):
    for number in range(1, 2):
        page_work_dict = get_page_work_dict(category, number)
        log(f'"{category.title}" 카테고리의 작업 목록 다운로드(Page: {number}/{last_page_number})')
        for pk, work in page_work_dict.items():
            if work.work_type == WorkListItem.WORK_TYPE_NORMAL and (pk in work_dict):
                log(f'PK({pk})에 해당하는 작업({work.title})은 이미 저장되어 있으므로 이후의 데이터는 저장된 정보를 사용합니다')
                break
            work_dict[pk] = work
        else:
            continue
        break
    pickle.dump(work_dict, open(pickle_name, 'wb'))
    return OrderedDict(sorted(work_dict.items()))


def main():
    categories = get_categories()
    category = select_category(categories)
    work_dict = get_work_dict(category, offline=True)

    workbook = xlsxwriter.Workbook('kmong.xlsx')
    header_format = workbook.add_format({
        'border': 1,
        'bg_color': '#C6EFCE',
        'bold': True,
        'text_wrap': True,
        'valign': 'vcenter',
        'align': 'center',
    })
    pk_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
    })
    content_format = workbook.add_format({
        'valign': 'vcenter',
    })
    worksheet = workbook.add_worksheet('첫번째시트')
    worksheet.set_row(0, 30)
    worksheet.set_column('B:B', 60)
    worksheet.set_column('C:C', 15)
    worksheet.set_column('D:D', 28)
    heading1 = 'PK'
    heading2 = '작업명'
    heading3 = '작업자'
    heading4 = '링크'
    worksheet.write('A1', heading1, header_format)
    worksheet.write('B1', heading2, header_format)
    worksheet.write('C1', heading3, header_format)
    worksheet.write('D1', heading4, header_format)
    start_row = 1
    for index, work in enumerate(work_dict.values()):
        row = index + start_row
        worksheet.set_row(row, 20)
        worksheet.write(row, 0, int(work.pk), pk_format)
        worksheet.write(row, 1, work.title, content_format)
        worksheet.write(row, 2, work.worker_username, content_format)
        worksheet.write(row, 3, f'https://kmong.com/gig/{work.pk}', content_format)
    worksheet.autofilter(0, 0, len(work_dict), 2)
    workbook.close()


if __name__ == '__main__':
    main()
