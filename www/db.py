import requests
from bs4 import BeautifulSoup as bs
import re
import lxml
import json
import sqlite3
import feedparser
from config import Config

db_path = Config.db_path

def add_abstract_pdf(title):
    print(title)
    # title = title.replace('.','').replace('.','').replace(' - ', ' ').replace(',',' ').replace('-',' ').replace(' ', '+')
    title = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", " ", title)
    title = '+'.join(title.split())
    print(title)
    text = requests.get(f'http://export.arxiv.org/api/query?search_query=ti:%22{title}%22').content
    feed = feedparser.parse(text)
    for entry in feed.entries:
        abstract = entry.summary
        abstract = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", " ", abstract)
        print(abstract)
        for link in entry.links:
            if link.rel == 'alternate':
                continue
            elif link.title == 'pdf':
                pdf = link.href.split('/')[-1]
                print(pdf)
                break
        break
    return abstract, pdf

def pdf_abs_openreview(ee, open_id):
    print(open_id)
    pdf = f'https://openreview.net/attachment?id={open_id}&name=original_pdf'
    try:
        text = requests.get(ee).content
        # print(text)
        text = bs(text, 'lxml')
        for div in text.find_all('li'):
            try:
                isabs = (div.find_all('strong', {'class': 'note-content-field'})[0].text=='Abstract:')
            except:
                isabs = False
            if isabs:
                cont = div.find_all('span',{'class':'note-content-value'})[0].text
                break
        cont = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", " ", cont)
        abstract = cont
    except:
        print('no abstract in openreview found')
    return abstract, pdf

def wrap(str):
    return '\''+str+'\''   


def add_papers_of_conf(conf,year):
    text = requests.get(f'https://dblp.uni-trier.de/search/publ/api?q=toc%3Adb/conf/{conf}/{conf}{year}.bht%3A&h=1000&format=json').content
    data = json.loads(text)['result']['hits']['hit']
    if conf in ['sigir','kdd','wsdm','recsys']:
        for record in data:
            print(record)
            title = record['info']['title']
            idx = record['@id']
            try:
                abstract, pdf = add_abstract_pdf(title)
                abstract, pdf = wrap(abstract),wrap(pdf)
            except:
                print(f'paper{idx}\'s pdf and abstract not found')
                abstract, pdf = 'NULL', 'NULL'
            add_paper(wrap(idx), wrap(title), year, wrap(conf), abstract, pdf)
    elif conf in ['iclr', 'icml', 'nips']:
        for record in data:
            print(record)
            title = record['info']['title']
            idx = record['@id']
            ee = record['info']['ee']
            open_id = re.findall('id=(.*)',ee)[0]
            try:
                abstract, pdf = pdf_abs_openreview(ee, open_id)
                abstract, pdf = wrap(abstract),wrap(pdf)
            except:
                print(f'paper{idx}\'s pdf and abstract not found')
                abstract, pdf = 'NULL', 'NULL'
            add_paper(wrap(idx), wrap(title), year, wrap(conf), abstract, pdf)
    


def create_table_confs():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('create table papers (idx char primary key, title text, year int, conf char, abstract text, pdf text)')
        cursor.close()
        conn.commit()
        conn.close()
    except:
        print('table papers already created')

def add_paper(idx, title, year, conf, abstract, pdf):
    print(title)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'insert into papers (idx, title, year, conf, abstract, pdf) values ({idx}, {title}, {year}, {conf},{abstract},{pdf})')
    cursor.close()
    conn.commit()
    conn.close()
    
create_table_confs()
for year in range(2021,2020,-1):
    add_papers_of_conf('nips', f'{year}')
