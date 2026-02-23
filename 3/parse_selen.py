import csv 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


username = "test_username"
password = "test_password_12345"
num_of_pages = 3
res = [["page_num", "quote", "author", "tags", "author_birth_date"]]

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

driver.get("https://quotes.toscrape.com/login")

wait.until(
    EC.element_to_be_clickable((By.ID, "username"))
).send_keys(username)
wait.until(
    EC.element_to_be_clickable((By.ID, "password"))
).send_keys(password)
wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
).click()

for page_num in range(num_of_pages):
    part_res = []
    
    wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "quote"))
    )
    quotes = driver.find_elements(By.CLASS_NAME, "quote")

    for quote in quotes:

        text_element = quote.find_element(By.CLASS_NAME, "text").text
        author_element = quote.find_element(By.CLASS_NAME, "author").text
        _, _, tags_element = quote.find_element(By.CLASS_NAME, "tags").text.partition("Tags: ")

        part_res.append([page_num+1, text_element, author_element, tags_element])
        
    author_links = driver.find_elements(By.LINK_TEXT, "(about)")

    for idx, link in enumerate(author_links):
        link.click()   
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "author-born-date"))
        )
        birth_date = driver.find_element(By.CLASS_NAME, "author-born-date").text
        part_res[idx].append(birth_date)
        driver.back()

    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li.next a"))
    ).click()

    res += part_res

with open('results.csv','w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(res[:])
  
