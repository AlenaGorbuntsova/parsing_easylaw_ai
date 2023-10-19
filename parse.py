import pickle
import itertools
import pandas as pd
from tqdm import tqdm
from time import sleep
from pathlib import Path
from selenium import webdriver
from joblib import Parallel, delayed
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


path = Path('data')

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')

n_workers = int(input('number of workers: '))


def chunks(xs, n):
    n = max(1, n)
    return [xs[i:i + n] for i in range(0, len(xs), n)]


def read_or_new_pickle(path, default_value = []):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:
        with open(path, "wb") as f:
            pickle.dump(default_value, f)
        print('New file has been created.')
        return []


def pop_elements(full_list, elements):
    for element in elements:
        full_list.remove(element)

 
def get_cases_by_word(search_term, driver_):
    def get_content_of_case(driver_):
        table_len = pd.read_html(driver_.find_element(By.CSS_SELECTOR, f'table').get_attribute('outerHTML'))[0].shape[0]


        content = {}
        for i in range(1, table_len + 1):
            header = driver_.find_element(By.CSS_SELECTOR, f'#contents > table > tbody > tr:nth-child({i}) > td > b').text
            
            case_detail = driver_.find_element(By.XPATH, f'//*[@id="contents"]/table/tbody/tr[{i}]/td').text
            case_detail = case_detail.removeprefix(header + '\n')
            
            content[header] = case_detail

        return content
    
    
    driver_.get('https://www.easylaw.ai/')      # go to the site
    
    # search for word
    search_box_element = driver_.find_element(By.CSS_SELECTOR, 'textarea#comment2.form-control')
    search_box_element.send_keys(search_term)
    search_box_element.send_keys(Keys.RETURN)


    word_cases = []

    while 1:
        # print(driver_.find_element(By.CSS_SELECTOR, '.dataTables_info').text, end="\r")

        page_buttons = driver_.find_elements(By.CSS_SELECTOR, 'button.btn-link')

        if not page_buttons:
            break

        for button in page_buttons:
            # go to clicked case tab:
            button.click()
            if len(driver_.window_handles) > 1:
                driver_.switch_to.window(driver_.window_handles[-1])
            else:
                continue

            content = get_content_of_case(driver_)
            content['search_term'] = search_term
            word_cases.append(content)
            
            # close clicker case tab:
            driver_.close()
            driver_.switch_to.window(driver_.window_handles[0])

        try:
            driver_.find_element(By.CSS_SELECTOR, '.paginate_button.next.disabled')
            break
        except NoSuchElementException:
            pass

        driver_.find_element(By.CSS_SELECTOR, '.paginate_button.next').click()

    return word_cases


if __name__ == '__main__':
    path.mkdir(parents=True, exist_ok=True)


    words = read_or_new_pickle(path / 'remaining_words.pkl')
    for chunk_of_words in (pbar := tqdm(chunks(words, n_workers))):
        pbar.set_description(f"Current chunk: {chunk_of_words}")
        
        drivers = [webdriver.Chrome(options=chrome_options) for _ in range(n_workers)]

        parallel_cases = Parallel(n_jobs=-1, prefer="threads")(delayed(get_cases_by_word)(*z) for z in zip(chunk_of_words, drivers))


        cases = read_or_new_pickle(path / 'cases.pkl')
        with open(path / 'cases.pkl', 'wb') as f:
            pickle.dump(cases + list(itertools.chain(*parallel_cases)), f)
        del cases

        pop_elements(words, chunk_of_words)
        with open(path / 'remaining_words.pkl', 'wb') as f:
            pickle.dump(words, f)
        
        
        sleep(60)
