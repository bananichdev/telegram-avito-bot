import undetected_chromedriver as uc
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent


class AvitoParse:
    def __init__(self, version_main: int = 117, url: str = '', items: list = ['оригинал'], count: int = 10):
        self.version_main = version_main
        self.url = url
        self.items = items
        self.count = count
        self.data = []

    def __set_up(self):
        options = Options()
        options.add_argument(f'user-agent={UserAgent(browsers=["chrome"]).random}')
        options.add_argument('--headless')
        system = os.getenv('SYSTEM')
        if system == 'linux':
            options.binary_location = 'app/parser/chrome-linux64/chrome'
        else:
            options.binary_location = 'app/parser/chrome-win64/chrome.exe'
        self.driver = uc.Chrome(
            version_main=self.version_main,
            options=options,
            driver_executable_path=f'app/parser/chromedriver-{system}64/chromedriver'
        )

    def __get_url(self):
        self.driver.get(self.url)

    def __paginator(self):
        while True:
            self.__parse_page()
            self.count -= 1
            if not self.driver.find_elements(By.CSS_SELECTOR, value='[data-marker="pagination-button/nextPage"]'):
                break
            if self.count == 0:
                break
            self.driver.find_element(By.CSS_SELECTOR, value='[data-marker="pagination-button/nextPage"]').click()

    def __parse_page(self):
        cards = self.driver.find_elements(By.CSS_SELECTOR, value='[data-marker="item"]')
        for card in cards:
            name = card.find_element(By.CSS_SELECTOR, value='[itemprop="name"]').text
            price = card.find_element(By.CSS_SELECTOR, value='[itemprop="price"]').get_attribute('content')
            description = card.find_element(By.CSS_SELECTOR, value='[class*="item-description"]').text
            url = card.find_element(By.CSS_SELECTOR, value='[data-marker="item-title"]').get_attribute('href')
            if any(word.lower() in description.lower() for word in self.items) and len(description) <= 250 and all(word not in description.lower() for word in ('качеств', 'люкс', 'материал')) and all(word not in name.lower() for word in ('качеств', 'люкс', 'материал')):
                data = {
                    'name': name,
                    'price': price,
                    'description': description,
                    'url': url
                }
                self.data.append(data)

    def __parse_first_element(self):
        name = self.driver.find_element(By.XPATH, value='//h3[@itemprop="name"]').text
        price = self.driver.find_element(By.CSS_SELECTOR, value='[itemprop="price"]').get_attribute('content')
        description = self.driver.find_element(By.CSS_SELECTOR, value='[class*="item-description"]').text
        url = self.driver.find_element(By.CSS_SELECTOR, value='[data-marker="item-title"]').get_attribute('href')
        if all(word not in description.lower() for word in ('качеств', 'люкс', 'материал')) and all(word not in name.lower() for word in ('качеств', 'люкс', 'материал')):
            self.data = {
                'name': name,
                'price': price,
                'description': description,
                'url': url
            }

    def __quit(self):
        self.driver.close()
        self.driver.quit()

    def set_up(self):
        self.__set_up()
        self.__get_url()

    def quit(self):
        self.__quit()

    def parse(self):
        self.__set_up()
        self.__get_url()
        self.__paginator()
        self.__quit()
        return self.data

    def notifications(self):
        self.driver.refresh()
        self.__parse_first_element()
        if self.data:
            return self.data
