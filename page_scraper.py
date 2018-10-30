import requests
from bs4 import BeautifulSoup

import time
import random

import sys
import os

BASE_URL = 'https://www.lds.org'
DIRECTORY = 'talks'
TIMEOUT = 5

os.makedirs(DIRECTORY, exist_ok=True)


class Talk:
    def __init__(self, title, author, author_role, body):
        self.title = title
        self.author = author
        self.author_role = author_role
        self.body = body

    def write(self, directory='.', prefix=''):
        filename = prefix + self.title + '-' + self.author
        full_filename = os.path.join(directory, filename)
        with open(full_filename, 'w') as outfile:
            outfile.write(self.body)

def random_wait():
    time.sleep(random.uniform(1,3))

def get_text_if_has(soup, tag, class_=None, id_=None, default=None):
    kwargs = {'name': tag,
              'class_': class_,
              'id': id_}
    kwargs = {k:v for k, v in kwargs.items() if v is not None}

    tag = soup.find(**kwargs)
    if tag:
        return tag.text
    else:
        return default

next_link = '/languages/zhs/content/general-conference/2017/10/the-plan-and-the-proclamation'
url = BASE_URL + next_link

def get_all_conference():
    conference_urls = ['https://www.lds.org/languages/zhs/item/general-conference/2018/04',
                       'https://www.lds.org/languages/zhs/item/general-conference/2017/10',
                       'https://www.lds.org/languages/zhs/item/general-conference/2017/04',
                       'https://www.lds.org/languages/zhs/item/general-conference/2016/10',
                       'https://www.lds.org/languages/zhs/item/general-conference/2016/04',
                       'https://www.lds.org/languages/zhs/item/general-conference/2015/10',
                       'https://www.lds.org/languages/zhs/item/general-conference/2015/04',
                       'https://www.lds.org/languages/zhs/item/general-conference/2014/10',
                      ]
    for url in conference_urls:
        directory = url[-7:-3] + '-' + url[-2:]
        get_general_conference(url, directory)

def get_general_conference(start_url, directory=''):
    directory = os.path.join(DIRECTORY, directory)
    print('Scraping', start_url)
    print('Contents saved at:', directory)
    os.makedirs(directory, exist_ok=True)
    i = 0
    cur_url = start_url
    # cur_url = BASE_URL + '/languages/zhs/content/general-conference/2017/10/womens-session'
    # cur_url = 'https://www.lds.org/languages/zhs/content/general-conference/2017/10/love-one-another-as-he-has-loved-us'

    while True:
        try:
            talk, next_url = get_text_and_next(cur_url)
        except Exception as e:
            print(e)
            print(cur_url)
            sys.exit(1)

        if not talk:
            print('Nothing at:', cur_url)
        else:
            print('talk', i)
            talk.write(directory=directory, prefix=str(i).zfill(2))
            i+=1
        cur_url = next_url
        if next_url is None:
            break

def get_text_and_next(url):
    page = None
    i = 1

    while not page:
        try:
            page = requests.get(url, timeout=TIMEOUT)
            random_wait()
        except requests.exceptions.Timeout as e:
            print(e)
            print(url)
            print('  retry:', i)
            i += 1
    soup = BeautifulSoup(page.content, 'html.parser')
    next_link = None
    for span_tag in soup.findAll('span'):
        if 'nextLink' in ' '.join(span_tag.get('class', '')):
            next_link = span_tag.a.get('href')

    talk = parse_general_conference(soup)
    next_url = (BASE_URL + next_link) if next_link else None
    return talk, next_url

def parse_general_conference(soup):
    body = soup.find('div', class_='body')

    #print('title')
    title = get_text_if_has(body, tag='h1', id_='title1', default='')
    #print('author')
    author = get_text_if_has(body, tag='p', class_='author-name', default='')
    #print('author_role')
    author_role = get_text_if_has(body, tag='p', class_='author-role', default='')
    if not title or not author:
        return None

    talk = {'title':title,
            'author': author,
            'author_role':author_role}

    body_block = body.find('div', class_='body-block')

    paragraphs = []
    for tag in body_block:
        if tag.name == 'p':
            paragraphs.append(tag.text)
        elif tag.name == 'section':
            paragraphs.append('\n'+tag.header.text)
            for p in tag.findAll('p'):
                paragraphs.append(p.text)
        elif tag.name == 'ul' or tag.name == 'div':
            for p in tag.findAll('p'):
                paragraphs.append(p.text)
                #print('~')
                #print(p.text)
                #print('~')
        elif tag.find('img'):
            pass
        else:
            print('unknown tag', tag.name)
            print(tag)

    header = f'{title}\n\n{author}\n{author_role}\n\n'
    talk['body'] = header + '\n\n'.join(paragraphs)
    return Talk(**talk)
# paragraphs = [p.text for p in body_block.findAll('p')]




#text = body.block.text
