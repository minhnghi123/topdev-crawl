from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import json

driver = webdriver.Chrome()
url = "https://topdev.vn/viec-lam-it"
driver.get(url)
time.sleep(5)

job_links_set = set()
scroll_pause_time = 0.01
scroll_increment = 500
current_position = 0

while True:
    # Cuộn từng bước
    driver.execute_script(f"window.scrollTo(0, {current_position});")
    time.sleep(scroll_pause_time)
    current_position += scroll_increment

    # Lấy HTML và parse
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)

    # Lọc link công việc
    for link in links:
        href = link['href']
        job_links_set.add(f"https://topdev.vn{href}")
    
    print(f"Số lượng link hiện tại: {len(job_links_set)}")
    
    # Nếu đủ link, dừng
    if len(job_links_set) >= 1000:
        break
    
    # Kiểm tra nếu cuộn không thêm được gì nữa
    new_height = driver.execute_script("return document.body.scrollHeight")
    if current_position >= new_height:
        break

# Lưu ra file
job_links = list(job_links_set)
with open('job_links.json', 'w', encoding='utf-8') as f:
    json.dump(job_links, f, ensure_ascii=False, indent=4)

print(f"Tổng số link: {len(job_links)}")
driver.quit()
