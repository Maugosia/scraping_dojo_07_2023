from bs4 import BeautifulSoup
import json

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class Scraper:
    def __init__(self, url, proxy, out_file, loading_timeout=30):
        self.url = url
        self.proxy = proxy
        self.output_file = out_file
        self.timeout = loading_timeout

    def get_data_from_url(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        options.add_argument('--proxy-server=%s' % self.proxy)
        driver = webdriver.Firefox(options=options)
        driver.get(self.url)

        is_next_page = True
        page_counter = 1
        while is_next_page:
            print("getting data from page {} : ".format(page_counter), end="  ")
            self.parse_page(driver)
            try:
                next_link = driver.find_element(By.PARTIAL_LINK_TEXT, 'Nex')
            except NoSuchElementException:
                is_next_page = False

            else:
                ActionChains(driver).scroll_to_element(next_link).move_to_element(next_link)
                next_link.click()
                is_next_page = True
                page_counter += 1
        driver.quit()

    def parse_page(self, driver):
        try:
            element = WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "quote"))
            )
        except TimeoutException:
            print("found no quotes due to waiting timeout, try setting higher waiting_timeout param")
        else:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            quote_list = soup.find_all('div', class_='quote')
            print(" {}  new quotes".format(len(quote_list)))

            for quote_data in quote_list:
                dict = self.extract_data_from_quote(quote_data)
                with open(self.output_file, "a") as outfile:
                    json.dump(dict, outfile, indent=4, ensure_ascii=True)

    @staticmethod
    def extract_data_from_quote(website_quote):
        text_data = website_quote.find('span', class_='text').get_text(strip=True)
        text_data_cleaned = text_data.replace('”', '').replace('\u201c', '')

        author_data = website_quote.find('small', class_='author').get_text(strip=True)

        tags_all = website_quote.find('div', class_='tags')
        tags_data = tags_all.find_all('a', class_='tag')
        tags = [tag.get_text(strip=True) for tag in tags_data]

        output_dict = {
            "text": text_data_cleaned,
            "by": author_data,
            "tags": tags
        }

        return output_dict
