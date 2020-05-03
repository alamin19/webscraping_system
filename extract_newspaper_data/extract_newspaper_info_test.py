#coding: utf-8
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from logs.logHandler import LogHelper
import requests
import sys
from urllib.parse import urlparse
import json
# import MySQLdb
import mysql.connector



class ExtractProthomalo:
    def __init__(self):
        self.logger = LogHelper().create_rotating_log('newspaper', 'extract_newspaper_info')
        self.newsppr_urls = [
            {'name': 'prothomalo', 'url': 'https://www.prothomalo.com/', 'prothomalo_logo_url':'https://paloimages.prothom-alo.com/contents/themes/public/style/images/Prothom-Alo.png'},
            {'name': 'kalerkantho', 'url': 'https://www.kalerkantho.com/', 'kalerkantho_logo_url': 'https://www.kalerkantho.com/assets/site/img/logo.png'},
            {'name': 'banglatribune', 'url': 'https://www.banglatribune.com/', 'banglatribune_logo_url': 'https://cdn.banglatribune.com/contents/themes/public/style/images/logo_bati.png'},
            {'name': 'ntvbd', 'url': 'https://www.ntvbd.com/', 'ntvbd_logo_url': 'https://www.ntvbd.com/sites/all/themes/sloth/logo.png'},
            {'name': 'jugantor', 'url': 'https://www.jugantor.com/', 'jugantor_logo_url': 'https://www.jugantor.com/templates/jugantor-v2/images/logo_main.png?v=1'},
            {'name': 'jagonews24', 'url': 'https://www.jagonews24.com/', 'jugonews24_logo_url': 'https://cdn.jagonews24.com/media/common/logo.png'}
            # {'name': }
        ]

        self.NEWSDB_HOST = 'localhost'
        self.NEWSDB_USER = 'root'
        self.NEWSDB_PASSWORD = ''
        self.NEWSDB_DATABASE = 'newspaper'

    def start_process(self):
        msg = "Going to start process for extracting news article information from Newspapers."
        self.logger.info(msg)
        prothomalo_urls = []
        prothomalo_ad = []
        ntvbd_urls = []
        ntvbd_ad = []
        jugantor_urls = []
        jugantor_ad = []
        banglatribune_urls = []
        banglatribune_ad = []
        kalerkantho_urls = []
        kalerkantho_ad = []
        jagonews24_urls = []
        jagonews24_ad = []

        try:
            for newsppr_url in self.newsppr_urls:
                print(newsppr_url['url'])
                page = requests.get(newsppr_url['url'])
                soup = BeautifulSoup(page.content, 'lxml')
                # print(soup)
                a_data = soup.find_all('a')
                # print(a_data)
                for data in a_data:
                    try:
                        a_url = data['href']
                        # print("------------------", data['href'])
                        is_valid = self.is_absolute(str(a_url))
                        if is_valid is False:
                            parsed_uri = urlparse(str(newsppr_url['url']))
                            domain_name = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
                            if a_url.startswith("/") is True:
                                vacancy_url = str(domain_name) + str(a_url)
                            else:
                                vacancy_url = str(domain_name) + '/' + str(a_url)
                        else:
                            vacancy_url = str(a_url)
                        print(vacancy_url)
                        if str(newsppr_url['name']) == 'prothomalo':
                            if 'article/' in str(vacancy_url):
                                print("vacancy_url --->>> ", vacancy_url)
                                vacancy_url = vacancy_url.rsplit('/', 1)[0]
                                vacancy_url = str(vacancy_url)+"/"
                                print(vacancy_url)
                                prothomalo_urls.append(vacancy_url)
                        elif newsppr_url['name'] == 'kalerkantho':
                            if 'online/' in str(vacancy_url):
                                if 'facebook' not in str(vacancy_url) and 'twitter' not in str(vacancy_url) and 'youtube' not in str(vacancy_url) and 'google' not in str(vacancy_url):
                                    for v in vacancy_url:
                                        if v.isdigit():
                                            kalerkantho_urls.append(vacancy_url)
                        elif newsppr_url['name'] == 'banglatribune':
                            if 'news/' in str(vacancy_url):
                                print(vacancy_url)
                                banglatribune_urls.append(vacancy_url)
                        elif newsppr_url['name'] == 'ntvbd':
                            print(vacancy_url)
                            ntvbd_urls.append(vacancy_url)
                        elif newsppr_url['name'] == 'jugantor':
                            if '/people' not in str(vacancy_url):
                                if 'facebook' not in str(vacancy_url) and 'twitter' not in str(vacancy_url) and 'youtube' not in str(vacancy_url) and 'google' not in str(vacancy_url):
                                    for v in vacancy_url:
                                        if v.isdigit():
                                            vacancy_url = vacancy_url.rsplit('/', 1)[0]
                                            vacancy_url = str(vacancy_url) + "/"
                                            print(vacancy_url)
                                            if vacancy_url not in jugantor_urls:
                                                jugantor_urls.append(vacancy_url)
                        elif newsppr_url['name'] == 'jagonews24': 
                            if 'article/' in str(vacancy_url) or 'news/' in str(vacancy_url) or 'sports/' in str(vacancy_url) or 'entertainment/' in str(vacancy_url) or 'photo-feature/' in str(vacancy_url) or 'health/' in str(vacancy_url):
                                for v in vacancy_url:
                                    if v.isdigit():
                                        vacancy_url = vacancy_url.rsplit('/', 1)[0]
                                        vacancy_url = str(vacancy_url) + "/"
                                        print(vacancy_url)
                                        if str(vacancy_url) not in jagonews24_urls:
                                            jagonews24_urls.append(vacancy_url)
                    except:
                        print(sys.exc_info())
                        continue

            print("length of prothomalo_urls --- >>> ", len(prothomalo_urls))
            for i in prothomalo_urls:
                try:
                    print(i)
                    pr_article_details = self.get_article_details_prothomalo(i)
                    if pr_article_details is None or len(pr_article_details) == 0:
                        continue
                    if len(pr_article_details) > 0 or pr_article_details is not None:
                        ar_url = pr_article_details['url']
                        print("url --------------->>>>>>>>>>>>>>> ", ar_url)
                        is_exist = self.match_existing_article_mysql(ar_url)
                        if is_exist < 1:
                            if pr_article_details['image_url'] is not None:
                                # prothomalo_ad.append(pr_article_details)
                                self.insert_article_details_mysql(pr_article_details)
                            else:
                                self.logger.info(str(pr_article_details['url']))
                        else:
                            print('--------------------------------------------------------------------------------------------------',is_exist)
                            print("is_exist ---- >>>>> ", is_exist)

                            continue
                    else:
                        print("--------------------------")



                except:
                    print(sys.exc_info())

            for i in ntvbd_urls:
                print(i)
                pr_article_details = self.get_article_details_ntvbd(i)
                print(pr_article_details)
                if pr_article_details is None or len(pr_article_details) == 0:
                    continue
                if len(pr_article_details) != 0 or pr_article_details is not None:
                    ntvbd_ad.append(pr_article_details)
                    ar_url = pr_article_details['url']
                    print("url --------------->>>>>>>>>>>>>>> ", ar_url)
                    is_exist = self.match_existing_article_mysql(ar_url)
                    if is_exist < 1:
                        if pr_article_details['image_url'] is not None:
                            # prothomalo_ad.append(pr_article_details)
                            self.insert_article_details_mysql(pr_article_details)
                        else:
                            self.logger.info(str(pr_article_details['url']))
                    else:
                        print(
                            '--------------------------------------------------------------------------------------------------',
                            is_exist)
                        print("is_exist ---- >>>>> ", is_exist)

                        continue
                else:
                    continue

            for i in jugantor_urls:
                print(i)
                pr_article_details = self.get_article_details_jugantor(i)
                if pr_article_details is None or len(pr_article_details) == 0:
                    continue
                if len(pr_article_details) != 0 or pr_article_details is not None:
                    jugantor_ad.append(pr_article_details)
                    ar_url = pr_article_details['url']
                    print("url --------------->>>>>>>>>>>>>>> ", ar_url)
                    is_exist = self.match_existing_article_mysql(ar_url)
                    if is_exist < 1:
                        if pr_article_details['image_url'] is not None:
                            # prothomalo_ad.append(pr_article_details)
                            self.insert_article_details_mysql(pr_article_details)
                        else:
                            self.logger.info(str(pr_article_details['url']))
                    else:
                        print(
                            '--------------------------------------------------------------------------------------------------',
                            is_exist)
                        print("is_exist ---- >>>>> ", is_exist)

                        continue

            for i in banglatribune_urls:
                print(i)
                pr_article_details = self.get_article_details_banglatribune(i)
                if pr_article_details is None or len(pr_article_details) == 0:
                    continue
                if len(pr_article_details) != 0 or pr_article_details is not None:
                    banglatribune_ad.append(pr_article_details)
                    ar_url = pr_article_details['url']
                    print("url --------------->>>>>>>>>>>>>>> ", ar_url)
                    is_exist = self.match_existing_article_mysql(ar_url)
                    if is_exist < 1:
                        if pr_article_details['image_url'] is not None:
                            # prothomalo_ad.append(pr_article_details)
                            self.insert_article_details_mysql(pr_article_details)
                        else:
                            self.logger.info(str(pr_article_details['url']))
                    else:
                        print(
                            '--------------------------------------------------------------------------------------------------',
                            is_exist)
                        print("is_exist ---- >>>>> ", is_exist)

                        continue

            for i in kalerkantho_urls:
                print(i)
                pr_article_details = self.get_article_details_kalerkantho(i)
                if pr_article_details is None or len(pr_article_details) == 0:
                    continue
                if len(pr_article_details) != 0 or pr_article_details is not None:
                    kalerkantho_ad.append(pr_article_details)
                    ar_url = pr_article_details['url']
                    print("url --------------->>>>>>>>>>>>>>> ", ar_url)
                    is_exist = self.match_existing_article_mysql(ar_url)
                    if is_exist < 1:
                        if pr_article_details['image_url'] is not None:
                            # prothomalo_ad.append(pr_article_details)
                            self.insert_article_details_mysql(pr_article_details)
                        else:
                            self.logger.info(str(pr_article_details['url']))
                    else:
                        print(
                            '--------------------------------------------------------------------------------------------------',
                            is_exist)
                        print("is_exist ---- >>>>> ", is_exist)

                        continue

            for i in jagonews24_urls:
                print(i)
                pr_article_details = self.get_article_details_jagonews24(i)
                if pr_article_details is None or len(pr_article_details) == 0:
                    continue
                if len(pr_article_details) != 0 or pr_article_details is not None:
                    jagonews24_ad.append(pr_article_details)
                    ar_url = pr_article_details['url']
                    print("url --------------->>>>>>>>>>>>>>> ", ar_url)
                    is_exist = self.match_existing_article_mysql(ar_url)
                    if is_exist < 1:
                        if pr_article_details['image_url'] is not None:
                            # prothomalo_ad.append(pr_article_details)
                            self.insert_article_details_mysql(pr_article_details)
                        else:
                            self.logger.info(str(pr_article_details['url']))
                    else:
                        print(
                            '--------------------------------------------------------------------------------------------------',
                            is_exist)
                        print("is_exist ---- >>>>> ", is_exist)

                        continue


            # print("length of all_urls --- >>> ", len(jagonews24_urls))

        except:
            self.logger.error(sys.exc_info())

    def get_article_details_prothomalo(self, url):
        image_url = None
        prothomalo_article_details = {}
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'lxml')
            try:
                title = "".join([p.text for p in soup.find_all('h1', class_='title mb10')])
                title = title.encode('utf-8')
                print(title)
            except:
                return None
            try:
                published_date = "".join([p.text for p in soup.find_all('span', itemprop='datePublished')])
                published_date = published_date.encode('utf-8')
                print(published_date)
            except:
                return None
            try:
                image_details = soup.find_all('img', class_='jwMediaContent image aligncenter')
                if len(image_details) == 0:
                    image_details = soup.find_all('img', class_='jwMediaContent image alignleft')
                for i in image_details:
                    try:
                        image_url = i['src']
                        print("image_url ---- >>> ", image_url)
                        if image_url is None:
                            return None
                    except:
                        return None
                print("direct ----------------->>>>>>>>>>> ", image_url)
            except:
                return None
            try:
                article_desc = "".join([p.text for p in soup.find_all('div', itemprop='articleBody')])
                article_desc = article_desc.replace("\n", "<br/>").replace("\r", "").replace("\t", "").replace("<br>",
                                                                                                               "<br/>")
                article_desc = article_desc.encode('utf-8')
                print(article_desc.strip())
            except:
                return None

            prothomalo_article_details = {
                'title': title,
                'image_url': image_url,
                'published_date': published_date,
                'description': article_desc,
                'logo': self.newsppr_urls[0]['prothomalo_logo_url'],
                'newspaper_name': 'prothomalo',
                'url':url,
            }

        except:
            print(sys.exc_info())
            return None
        return prothomalo_article_details

    def get_article_details_kalerkantho(self, url):
        article_details = {}
        image_url = None
        title = None
        published_date = None
        article_desc = None
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'lxml')
            try:
                title = soup.find("meta",  property="og:title")['content']
                title = str(title).split('|')[0].strip()
                title = title.encode('utf-8')
                print("------------", title)
                print(title)
            except:
                print(sys.exc_info())
                return None
            try:
                published_date = soup.find_all("p", class_="text-left pull-left n_author")
                published_date = published_date[1]
                published_date = published_date.get_text()
                published_date = str(published_date).split('|')[0].strip()
                published_date = published_date.encode('utf-8')
                print(published_date)
            except:
                return None
            try:
                image_details = soup.find_all('img', class_='img')
                for image in image_details:
                    try:
                        image_url = image['src']
                    except:
                        return None
                image_url = image_url.encode('utf-8')
                print(image_url)
            except:
                return None
            try:
                article_desc = ''
                article = soup.find("div", {"class": "some-class-name2"}).findAll('p')
                for element in article:
                    article_desc += '\n' + ''.join(element.findAll(text=True))
                article_desc = article_desc.replace("\n", "<br/>").replace("\r", "").replace("\t", "").replace("<br>",
                                                                                                               "<br/>")
                article_desc = article_desc.encode('utf-8')
                print(article_desc)
            except:
                return None
            article_details = {
                'title': title,
                'published_date': published_date,
                'image_url': image_url,
                'description': article_desc,
                'newspaper_name': 'Kalerkantho',
                'logo': self.newsppr_urls[1]['kalerkantho_logo_url'],
                'url': url
            }
        except:
            print(sys.exc_info())
            return None
        return article_details

    def get_article_details_banglatribune(self, url):
        image_url = None
        title = None
        published_date = None
        article_desc = None
        article_details = {}
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'lxml')
            try:
                title = soup.find('title').string
                title = title.encode('utf-8')
                print(title)
            except:
                return None
            try:
                published_date = soup.find_all("span", class_="time")

                published_date = published_date[1]
                published_date = published_date.get_text()
                # print(published_date)
                published_date1 = str(published_date).split(':')[1]
                published_date2 = str(published_date).split(':')[2]
                published_date = str(published_date1) + ":" + str(published_date2)
                published_date = published_date.strip()
                published_date = published_date.encode('utf-8')
                print(published_date.strip())
            except:
                return None
            try:
                image_details = soup.find_all('img', itemprop='image')
                for image in image_details:
                    try:
                        image_url = image['src']
                    except:
                        return None
                image_url = image_url.encode('utf-8')
                print(image_url)
            except:
                return None
            try:
                article_desc = ''
                article = soup.find("div", {"itemprop": "articleBody"}).findAll('p')
                for element in article:
                    article_desc += '\n' + ''.join(element.findAll(text=True))
                article_desc = article_desc.replace("\n", "<br/>").replace("\r", "").replace("\t", "").replace("<br>",
                                                                                                               "<br/>")
                article_desc = article_desc.encode('utf-8')
                print(article_desc)
            except:
                return None

            article_details = {
                'title': title,
                'published_date': published_date,
                'image_url': image_url,
                'description': article_desc,
                'newspaper_name': 'Bangla Tribune',
                'logo': self.newsppr_urls[2]['banglatribune_logo_url'],
                'url': url
            }
        except:
            print(sys.exc_info())
            return None
        return article_details

    def get_article_details_ntvbd(self, url):
        image_url = None
        title = None
        published_date = None
        image_url = None
        article_details = {}
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'lxml')
            results = soup.find('script', attrs={'type': 'application/ld+json'}).text
            news_details = json.loads(results)
            print(news_details)
            try:
                news_details = news_details['@graph']
            except:
                return None
            print(news_details)
            for news in news_details:
                try:
                    print(news)
                    news_type = news['@type']
                    if news_type == 'NewsArticle':
                        try:
                            title = news['headline']
                            title = title.encode('utf-8')
                            print(title)
                        except:
                            return None
                        try:
                            published_date = news['datePublished'].replace('T', ' ').replace('Z', '').split('+')[0]
                            published_date = published_date.encode('utf-8')
                            print(published_date)
                        except:
                            return None
                        try:
                            image_url = news['image']['url']
                            image_url = image_url.encode('utf-8')
                            print(image_url)
                        except:
                            return None
                    else:
                        return None
                except:
                    return None
            try:
                article_desc = ''

                article = soup.find("div", class_="section-content pl-30 pr-30 pb-20 text-justify").findAll('p')
                for element in article:
                    article_desc += '\n' + ''.join(element.findAll(text=True))
                article_desc = article_desc.replace("\n", "<br/>").replace("\r", "").replace("\t", "").replace("<br>",
                                                                                                               "<br/>")
                article_desc = article_desc.encode('utf-8')
                print(article_desc)
            except:
                return None

            article_details = {
                'title': title,
                'published_date': published_date,
                'image_url': image_url,
                'description': article_desc,
                'newspaper_name':'ntvbd',
                'logo': self.newsppr_urls[3]['ntvbd_logo_url'],
                'url': url,
            }

        except:
            print(sys.exc_info())
            return None
        return article_details

    def get_article_details_jugantor(self, url):
        image_url = None
        title = None
        published_date = None
        image_url = None
        article_details = {}
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'lxml')
            for match in soup.findAll('span'):
                match.clear()
            try:
                title = soup.find('title').string
                title = title.encode('utf-8')
                print(title)
            except:
                return None

            try:
                published_date = soup.find("div", class_="rpt_name").get_text()
                published_date = str(published_date).split('|')[0].strip()
                published_date = published_date.encode('utf-8')
                print(published_date)

            except:
                return None
            try:
                image_details = soup.find('div', class_='img').findAll('a')[0]
                for image in image_details:
                    try:
                        image_url = image['src']
                    except:
                        return None
                is_valid = self.is_absolute(str(image_url))
                if is_valid is False:
                    parsed_uri = urlparse(str(url))
                    domain_name = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
                    if image_url.startswith("/") is True:
                        image_url = str(domain_name) + str(image_url)
                    else:
                        image_url = str(domain_name) + '/' + str(image_url)
                else:
                    image_url = str(image_url)
                image_url = image_url.encode('utf-8')
                print(image_url)
            except:
                return None

            try:
                article_desc = ''
                article = soup.find("div", class_="dtl_section").findAll('p')
                for element in article:
                    article_desc += '\n' + ''.join(element.findAll(text=True))
                article_desc = article_desc.replace("\n", "<br/>").replace("\r", "").replace("\t", "").replace("<br>",
                                                                                                               "<br/>")
                article_desc = article_desc.encode('utf-8')
                print(article_desc)

            except:
                return None
            article_details = {
                'title': title,
                'published_date': published_date,
                'image_url': image_url,
                'description': article_desc,
                'newspaper_name': 'Jugantor',
                'logo': self.newsppr_urls[4]['jugantor_logo_url'],
                'url': url
            }
        except:
            print(sys.exc_info())
            return None
        return article_details

    def get_article_details_jagonews24(self, url):
        image_url = None
        title = None
        published_date = None
        article_desc = None

        article_details = {}
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'lxml')
            try:
                title = soup.find('title').string
                title = title.encode('utf-8')
                print(title)
            except:
                return None

            try:
                published_date = soup.find("span", class_="small text-muted time-with-author").get_text()
                published_date = str(published_date).split('প্রকাশিত:')[1].strip()
                published_date = published_date.encode('utf-8')

            except:
                return None
            try:
                image_details = soup.find('div', class_='featured-image').findAll('img')[0]

                try:
                    image_url = image_details['data-src']
                except:
                    return None

                is_valid = self.is_absolute(str(image_url))
                if is_valid is False:
                    parsed_uri = urlparse(str(url))
                    domain_name = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
                    if image_url.startswith("/") is True:
                        image_url = str(domain_name) + str(image_url)
                    else:
                        image_url = str(domain_name) + '/' + str(image_url)
                else:
                    image_url = str(image_url)
                image_url = image_url.encode('utf-8')
                print(image_url)
            except:
                return None
            #
            try:
                article_desc = ''
                article = soup.find("div", class_="content-details").findAll('p')
                for element in article:
                    article_desc += '\n' + ''.join(element.findAll(text=True))
                article_desc = article_desc.replace("\n", "<br/>").replace("\r", "").replace("\t", "").replace("<br>", "<br/>")
                article_desc = article_desc.encode('utf-8')
                print(article_desc)

            except:
                return None
            article_details = {
                'title': title,
                'published_date': published_date,
                'image_url': image_url,
                'description': article_desc,
                'newspaper_name': 'Jugonews24',
                'logo': self.newsppr_urls[5]['jugonews24_logo_url'],
                'url': url
            }
        except:
            print(sys.exc_info())
            self.logger.error(sys.exc_info())
            return None
        return article_details

    def is_absolute(self, url):
        return bool(urlparse(url).netloc)

    def insert_article_details_mysql(self, i):
        conn = mysql.connector.connect(host=self.NEWSDB_HOST, user=self.NEWSDB_USER, passwd=self.NEWSDB_PASSWORD,
                               db=self.NEWSDB_DATABASE, charset='utf8', use_unicode=True)

        cursor = conn.cursor()
        title = None
        image = None
        description = None
        logo = None
        newspaper_name = None
        url = None
        # for i in t:
        title = i['title']
        image = i['image_url']
        print("image --- >>>> ", image)
        published_date = i['published_date']
        description = i['description']
        logo = i['logo']
        newspaper_name = i['newspaper_name']
        url = i['url']

        query = u"""insert into scrapednews (title, description, url, image, logo, newspaper_name) values (%s, %s, %s, %s, %s, %s);"""

        try:
            cursor.execute("set names utf8;")
            cursor.execute(query, (title, description, url, image, logo, newspaper_name))
            conn.commit()

        except:
            print(sys.exc_info())
            self.logger.error(sys.exc_info())
        finally:
            cursor.close()
            conn.close()

    def get_article_details_mysql(self):
        conn = mysql.connector.connect(host=self.NEWSDB_HOST, user=self.NEWSDB_USER, passwd=self.NEWSDB_PASSWORD,
                               db=self.NEWSDB_DATABASE, charset='utf8', use_unicode=True)
        cursor = conn.cursor()

        try:
            query = "select * from scrapednews;"
            cursor.execute(query)
            rec = cursor.fetchall()
            print(rec)

        except:
            print(sys.exc_info())
            self.logger.error(sys.exc_info())
        finally:
            cursor.close()
            conn.close()

    def match_existing_article_mysql(self, url):
        conn = mysql.connector.connect(host=self.NEWSDB_HOST, user=self.NEWSDB_USER, passwd=self.NEWSDB_PASSWORD,
                               db=self.NEWSDB_DATABASE, charset='utf8', use_unicode=True)
        cursor = conn.cursor()
        is_matched = 0
        try:
            query = "select count(*) from scrapednews where url='{0}';".format(url)
            print(query)
            cursor.execute(query)
            rec = cursor.fetchone()
            is_matched = rec[0]

        except:
            print(sys.exc_info())
            self.logger.error(sys.exc_info())
        finally:
            cursor.close()
            conn.close()
        return is_matched


if __name__ == '__main__':
    objEP = ExtractProthomalo()
    url = 'https://www.prothomalo.com/bangladesh/article/1650523/%E0%A6%AE%E0%A6%BE%E0%A6%9D%E0%A7%87-%E0%A6%AE%E0%A6%BE%E0%A6%9D%E0%A7%87-%E0%A6%AD%E0%A7%9F-%E0%A6%B9%E0%A6%A4%E0%A7%8B-%E0%A6%B8%E0%A7%81%E0%A6%B8%E0%A7%8D%E0%A6%A5-%E0%A6%B9%E0%A7%9F%E0%A7%87-%E0%A6%AC%E0%A6%B2%E0%A6%B2%E0%A7%87%E0%A6%A8-%E0%A6%9A%E0%A6%BF%E0%A6%95%E0%A6%BF%E0%A7%8E%E0%A6%B8%E0%A6%95'
    objEP.start_process()
    # objEP.match_existing_article_mysql(url)

    # objEP.insert_article_details_mysql()
