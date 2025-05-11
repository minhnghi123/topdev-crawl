from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import json
# Khởi tạo trình duyệt
driver = webdriver.Chrome()  # hoặc Firefox

driver.get("https://accounts.topdev.vn/login/github")

time.sleep(3)

username_input = driver.find_element(By.ID, "login_field")
password_input = driver.find_element(By.ID, "password")

password_input.send_keys(Keys.RETURN)

time.sleep(5)


# Lấy mã nguồn HTML của trang
html = driver.page_source


# Mở trang web
url = "https://topdev.vn/viec-lam-it?src=topdev.vn&medium=mainmenu"
driver.get(url)

# Đợi trang tải xong (có thể điều chỉnh thời gian nếu cần)
time.sleep(5)

# Lấy mã nguồn HTML của trang
html = driver.page_source

# Phân tích HTML bằng BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Tìm tất cả các thẻ <a> có href bắt đầu bằng "/viec-lam/"

links = soup.find_all('a', href=True)
job_links = [f"https://topdev.vn{link['href']}" for link in links if link['href'].startswith('/viec-lam/')]

# Lưu danh sách các liên kết vào file JSON
output_file = 'job_links.json'
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(job_links, file, ensure_ascii=False, indent=4)

print(f"Danh sách liên kết đã được lưu vào {output_file}")