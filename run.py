from dotenv import load_dotenv
import os

from scraper import Scraper


def run_scrape():
    load_dotenv()
    proxy = os.getenv('PROXY')
    input_url = os.getenv('INPUT_URL')
    output_file = os.getenv('OUTPUT_FILE')

    if os.path.isfile(output_file):
        os.remove(output_file)

    scraper = Scraper(input_url, proxy, output_file, loading_timeout=15)
    scraper.get_data_from_url()


if __name__ == '__main__':
    run_scrape()
