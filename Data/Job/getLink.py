from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json

driver = webdriver.Chrome()
url = "https://topdev.vn/viec-lam-it/ho-chi-minh-kl79"
driver.get(url)
time.sleep(1)

job_links_set = set()  # Sử dụng set để loại bỏ các link trùng lặp
scroll_pause_time = 0.5
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
    job_items = soup.find_all('li', class_='mb-4 last:mb-0')  # Tìm các thẻ <li>

    for item in job_items:
        # Lấy tất cả các thẻ <a> trong thẻ <li>
        a_tags = item.find_all('a', href=True)
        for a_tag in a_tags:
            href = a_tag['href']
            # Xử lý link đầy đủ
            full_link = "https://topdev.vn" + href if href.startswith('/') else href
            job_links_set.add(full_link)  # Thêm link vào set

    print(f"Số lượng link hiện tại: {len(job_links_set)}")

    # Kiểm tra nếu cuộn không thêm được gì nữa
    new_height = driver.execute_script("return document.body.scrollHeight")
    if current_position >= new_height:
        break

# Lưu các link vào file JSON
job_links = list(job_links_set)  # Chuyển set thành danh sách
with open("job_links_full_hcm.json", "w", encoding="utf-8") as f:
    json.dump(job_links, f, ensure_ascii=False, indent=4)

print(f"Đã lưu {len(job_links)} link vào file job_links.json.")
driver.quit()