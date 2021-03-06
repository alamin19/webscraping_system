from bs4 import BeautifulSoup
from logs.logHandler import LogHelper
import requests
import sys
from urllib.parse import urlparse


class ExtractProthomalo:
    def __init__(self):
        self.logger = LogHelper().create_rotating_log('newspaper', 'banglatribune')
        self.newsppr_url = "https://www.banglatribune.com/"

    def start_process(self):
        msg = "Going to start process for extracting information for banglatribune Newspaper."
        self.logger.info(msg)
        all_urls = []

        try:
            page = requests.get(self.newsppr_url)
            soup = BeautifulSoup(page.content, 'lxml')
            a_data = soup.find_all('a')
            for data in a_data:
                try:
                    a_url = data['href']
                    if 'javascript' in str(a_url).lower():
                        continue
                    is_valid = self.is_absolute(str(a_url))
                    if is_valid is False:
                        parsed_uri = urlparse(str(self.newsppr_url))
                        domain_name = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
                        if a_url.startswith("/") is True:
                            vacancy_url = str(domain_name) + str(a_url)
                        else:
                            vacancy_url = str(domain_name) + '/' + str(a_url)
                    else:
                        vacancy_url = str(a_url)
                    if str(vacancy_url) not in all_urls:
                        if 'http://' not in str(vacancy_url).lower() and 'https://' not in str(vacancy_url).lower():
                            vacancy_url = 'https://' + str(vacancy_url)
                        else:
                            vacancy_url = str(vacancy_url)
                        print(vacancy_url)
                        all_urls.append(vacancy_url)
                except:
                    continue

            print(all_urls)
            print(len(all_urls))

        except:
            self.logger.error(sys.exc_info())

    def is_absolute(self, url):
        return bool(urlparse(url).netloc)


if __name__ == '__main__':
    objEP = ExtractProthomalo()
    objEP.start_process()
