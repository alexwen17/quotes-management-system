import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def run_scraper():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # 初始化資料庫
    conn = sqlite3.connect('quotes.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, author TEXT, tags TEXT)')
    
    driver.get("http://quotes.toscrape.com/js/")
    
    for page in range(5): # 抓取 5 頁
        time.sleep(1) # 等待 JS 渲染
        items = driver.find_elements(By.CLASS_NAME, "quote")
        for item in items:
            text = item.find_element(By.CLASS_NAME, "text").text
            author = item.find_element(By.CLASS_NAME, "author").text
            tags = ",".join([t.text for t in item.find_elements(By.CLASS_NAME, "tag")])
            cursor.execute("INSERT INTO quotes (text, author, tags) VALUES (?, ?, ?)", (text, author, tags))
        
        try:
            driver.find_element(By.CSS_SELECTOR, "li.next a").click()
        except: break
            
    conn.commit()
    conn.close()
    driver.quit()
    print("爬蟲完成，資料庫已就緒。")

if __name__ == "__main__":
    run_scraper()