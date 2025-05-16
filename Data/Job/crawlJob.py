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

time.sleep(30)

# # Nhập thông tin tài khoản
# username_input.send_keys("hophuoc98765432@gmail.com")  # Thay "your_username" bằng tên đăng nhập của bạn
# password_input.send_keys("")  # Thay "your_password" bằng mật khẩu của bạn



# Lấy mã nguồn HTML của trang
html = driver.page_source



# Đợi trang tải xong (có thể điều chỉnh thời gian nếu cần)

# Đường dẫn file chứa danh sách link
job_links_file = r"D:\16052025\topdev-crawl\Data\Job\job_links_full.json"
output_file = r"D:\16052025\topdev-crawl\Data\Job\company_info.json"

# Đọc danh sách link từ file JSON
with open(job_links_file, "r", encoding="utf-8") as f:
    job_links = json.load(f)

company_data = []

# Crawl từng link
for link in job_links:
    try:
        # Mở trang web
        url = link
        driver.get(url)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Trích xuất thông tin từ section id="detailJobHeader"
        job_section = soup.find('section', id='detailJobHeader')

        if job_section:
            # Tiêu đề công việc
            job_title = job_section.find('h1', class_='text-2xl font-bold text-black').text.strip() if job_section.find('h1', class_='text-2xl font-bold text-black') else None

            # Tên công ty
            company_name = job_section.find('p', class_='my-1 line-clamp-1 text-base font-bold text-[#F05C43]').text.strip() if job_section.find('p', class_='my-1 line-clamp-1 text-base font-bold text-[#F05C43]') else None

            # Địa chỉ
            address = job_section.find('span', class_='hover:text-[#DD3F24]').text.strip() if job_section.find('span', class_='hover:text-[#DD3F24]') else None

            # In thông tin
            print("Tiêu đề công việc:", job_title)
            print("Tên công ty:", company_name)
            print("Địa chỉ:", address)
        else:
            print("Không tìm thấy section id='detailJobHeader'")




        print(f"Đã crawl: {link}")
    except Exception as e:
        print(f"Lỗi khi crawl {link}: {e}")

# Lưu thông tin vào file JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(company_data, f, ensure_ascii=False, indent=4)

print(f"Đã lưu thông tin {len(company_data)} công ty vào file {output_file}.")

driver.quit()