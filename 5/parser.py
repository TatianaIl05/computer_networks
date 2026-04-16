import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Parser:
    def __init__(self):
        load_dotenv()
        self.driver = None
        self.config = self.load_config()
        
    def load_config(self):
        return {
            'username': os.getenv('QUOTES_USERNAME'),
            'password': os.getenv('QUOTES_PASSWORD'),
            'pages': int(os.getenv('PAGES', '3')),
            'headless': os.getenv('HEADLESS', 'true').lower() == 'true'
        }
    
    def create_driver(self):
        options = Options()
        
        if self.config['headless']:
            options.add_argument('--headless')
            options.add_argument('--window-size=1920,1080')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.binary_location = "/usr/bin/chromium"
        
        return webdriver.Chrome(options=options)
    
    def login(self, wait, url = "https://quotes.toscrape.com"):
        login_url = f"{url}/login"
        self.driver.get(login_url)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#username"))).send_keys(self.config['username'])
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#password"))).send_keys(self.config['password'])
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))).click()
    
    def get_author_birth_date(self, wait, author_link):
        try:
            author_link.click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".author-born-date")))
            birth_date = self.driver.find_element(By.CSS_SELECTOR, ".author-born-date").text
            self.driver.back()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))
            return birth_date
        except:
            return "N/A"
    
    def truncate_quote(self, text, max_sentences=2):
        sentences = text.replace('?', '.').replace('!', '.').split('.')
        truncated = '.'.join(sentences[:max_sentences]).strip()
        
        return truncated
    
    def scrape_page(self, wait, page_num):
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))
        quotes = self.driver.find_elements(By.CSS_SELECTOR, ".quote")
        
        all_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/author/']")
        author_links = [link for link in all_links if "(about)" in link.text]
        
        page_results = []
        
        for idx, quote in enumerate(quotes):
            text = self.truncate_quote(quote.find_element(By.CSS_SELECTOR, ".text").text)
            author = quote.find_element(By.CSS_SELECTOR, ".author").text
            tags = quote.find_element(By.CSS_SELECTOR, ".tags").text.replace("Tags: ", "")
            
            if idx < len(author_links):
                birth_date = self.get_author_birth_date(wait, author_links[idx])
            else:
                birth_date = "N/A"
            
            page_results.append((page_num, text, author, tags, birth_date))
        
        return page_results
    
    def go_to_next_page(self, wait, page_num, total_pages):
        if page_num < total_pages - 1:
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next > a")))
                next_button.click()
                return True
            except:
                return False
        return False
    
    def parse_quotes(self, url: str):
        if not self.config['username'] or not self.config['password']:
            raise ValueError("QUOTES_USERNAME and QUOTES_PASSWORD must be set in .env")
        
        results = []
        
        try:
            self.driver = self.create_driver()
            wait = WebDriverWait(self.driver, 10)
            
            self.login(wait, url)
            
            for page_num in range(self.config['pages']):
                page_quotes = self.scrape_page(wait, page_num + 1)
                results.extend(page_quotes)
                
                if not self.go_to_next_page(wait, page_num, self.config['pages']):
                    break
        
        except Exception as e:
            print(f"Error: {e}")
            raise
        
        finally:
            if self.driver:
                self.driver.quit()
        
        return results
    
    def close(self):
        if self.driver:
            self.driver.quit()
    
