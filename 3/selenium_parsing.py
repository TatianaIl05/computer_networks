import os
import csv

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def load_config():
    load_dotenv()

    return {
        'username': os.getenv('QUOTES_USERNAME'),
        'password': os.getenv('QUOTES_PASSWORD'),
        'pages': int(os.getenv('PAGES', '3')),
        'headless': os.getenv('HEADLESS', 'false').lower() == 'true'
    }


def create_driver(config):
    options = Options()
    
    if config['headless']:
        options.add_argument('--headless')
        options.add_argument('--window-size=1920,1080')
    
    options.add_argument('--no-sandbox')

    return webdriver.Chrome(options=options)


def login(driver, wait, config):
    driver.get("https://quotes.toscrape.com/login")
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#username"))).send_keys(config['username'])
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#password"))).send_keys(config['password'])
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))).click()


def get_author_birth_date(driver, wait, author_link):
    try:
        author_link.click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".author-born-date")))
        birth_date = driver.find_element(By.CSS_SELECTOR, ".author-born-date").text
        driver.back()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))
        return birth_date
    except:
        return "N/A"


def truncate_quote(text, max_sentences=2):
    sentences = text.replace('?', '.').replace('!', '.').split('.')
    truncated = '.'.join(sentences[:max_sentences]).strip()
    
    return truncated


def scrape_page(driver, wait, page_num):
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))
    quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")
    
    all_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/author/']")
    author_links = [link for link in all_links if "(about)" in link.text]
    
    page_results = []
    
    for idx, quote in enumerate(quotes):
        text = truncate_quote(quote.find_element(By.CSS_SELECTOR, ".text").text)
        author = quote.find_element(By.CSS_SELECTOR, ".author").text
        tags = quote.find_element(By.CSS_SELECTOR, ".tags").text.replace("Tags: ", "")
        
        if idx < len(author_links):
            birth_date = get_author_birth_date(driver, wait, author_links[idx])
        else:
            birth_date = "N/A"
        
        page_results.append([page_num, text, author, tags, birth_date])
    
    return page_results


def go_to_next_page(wait, page_num, total_pages):
    if page_num < total_pages - 1:
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next > a")))
            next_button.click()
            return True
        except:
            return False
    return False


def scrape_quotes():
    config = load_config()
    
    if not config['username'] or not config['password']:
        raise ValueError("QUOTES_USERNAME and QUOTES_PASSWORD must be set in .env")
    
    driver = None
    results = [["page_num", "quote", "author", "tags", "author_birth_date"]]
    
    try:
        driver = create_driver(config)
        wait = WebDriverWait(driver, 10)
        
        login(driver, wait, config)
        
        for page_num in range(config['pages']):
            page_results = scrape_page(driver, wait, page_num + 1)
            results.extend(page_results)
            
            if not go_to_next_page(wait, page_num, config['pages']):
                break
    
    except Exception as e:
        print(f"Error: {e}")
        raise
    
    finally:
        if driver:
            driver.quit()
    
    return results


def save_results(results):
    with open('results.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(results)

if __name__ == "__main__":
    data = scrape_quotes()
    save_results(data)
    
