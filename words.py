import pickle
import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

path = Path('data')

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')

if __name__ == '__main__':
    driver = webdriver.Chrome(options=chrome_options)

    driver.get('https://web.archive.org/web/20230205160246/https://studynow.ru/dicta/allwords')

    words_table = driver.find_element(By.CSS_SELECTOR, f'#wordlist').get_attribute('outerHTML')
    words_table = pd.concat(pd.read_html(words_table))
    
    driver.close()

    words = list(words_table[1])
    words = pd.Series(words).str.split(' ').str[0].drop_duplicates().tolist()

    with open(path / 'all_words.pkl', 'wb') as f:
        pickle.dump(words, f)
