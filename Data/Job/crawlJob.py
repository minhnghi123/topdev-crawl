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

# username_input = driver.find_element(By.ID, "login_field")
# password_input = driver.find_element(By.ID, "password")

# password_input.send_keys(Keys.RETURN)

time.sleep(40)

# # Nhập thông tin tài khoản
# username_input.send_keys("hophuoc98765432@gmail.com")  # Thay "your_username" bằng tên đăng nhập của bạn
# password_input.send_keys("")  # Thay "your_password" bằng mật khẩu của bạn

# Lấy mã nguồn HTML của trang
html = driver.page_source
# Đợi trang tải xong (có thể điều chỉnh thời gian nếu cần)

# Đường dẫn file chứa danh sách link
job_links_file = r"D:\git\topdev-crawl\Data\Job\job_links_full.json"
output_file = r"D:\git\topdev-crawl\Data\Job\job_info.json"

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

        # Tiêu đề công việc
        job_title = job_section.find('h1', class_='text-2xl font-bold text-black').text.strip() if job_section.find('h1', class_='text-2xl font-bold text-black') else None

        # Tên công ty
        company_name = job_section.find('p', class_='my-1 line-clamp-1 text-base font-bold text-[#F05C43]').text.strip() if job_section.find('p', class_='my-1 line-clamp-1 text-base font-bold text-[#F05C43]') else None

        # Địa chỉ ngắn (hiển thị)
        address = job_section.find('span', class_='hover:text-[#DD3F24]').text.strip() if job_section.find('span', class_='hover:text-[#DD3F24]') else None

        # Địa chỉ dài (tooltip, nếu có)
        address_long = None
        tooltip_div = job_section.find('div', {'data-testid': 'flowbite-tooltip'})
        if tooltip_div:
            # Lấy text trong div con (có thể chứa tiếng Anh và tiếng Việt, cách nhau bởi "/")
            address_long = tooltip_div.find('div', class_='relative z-20')
            address_long = address_long.text.strip() if address_long else tooltip_div.text.strip()

        main_info = soup.find('div', class_='flex flex-col self-stretch p-[25px] pb-2')
        if main_info:
            # Lương
            salary = None
            salary_tag = main_info.find('p', class_='text-primary')
            if salary_tag:
                salary = salary_tag.text.strip()

            # Thời gian đăng và hết hạn
            posted_time = None
            expired_time = None
            time_tag = main_info.find('div', class_='flex w-11/12 items-center text-[14px] font-[500] text-[#5D5D5D]')
            if time_tag:
                time_text = time_tag.get_text(separator=" ", strip=True)
                # Tách thời gian đăng và hết hạn
                if "và" in time_text:
                    parts = time_text.split("và")
                    posted_time = parts[0].replace("Đăng", "").strip()
                    expired_time = parts[1].replace("Công việc hết hạn trong", "").strip()
                else:
                    posted_time = time_text

            # Skills
            skills = []
            skill_tags = main_info.find_all('span', class_='whitespace-nowrap rounded border border-solid font-normal transition-all inline-flex items-center justify-center border-blue-light text-blue-dark bg-blue-light hover:border-blue-dark h-[1.625rem] px-2 text-xs md:h-7 md:px-2 md:text-sm')
            for tag in skill_tags:
                skills.append(tag.text.strip())

            # Năm kinh nghiệm
            exp = None
            exp_block = main_info.find('h3', string=lambda s: s and 'Năm kinh nghiệm' in s)
            if exp_block:
                exp_parent = exp_block.find_next_sibling('div')
                if exp_parent:
                    exp = exp_parent.text.strip()

            # Cấp bậc
            level = None
            level_block = main_info.find('h3', string=lambda s: s and 'Cấp bậc' in s)
            if level_block:
                level_parent = level_block.find_next_sibling('div')
                if level_parent:
                    level = level_parent.text.strip()

            # Loại hình
            job_type = None
            type_block = main_info.find('h3', string=lambda s: s and 'Loại hình' in s)
            if type_block:
                type_parent = type_block.find_next_sibling('div')
                if type_parent:
                    job_type = type_parent.text.strip()

            # Loại hợp đồng
            contract_type = None
            contract_block = main_info.find('h3', string=lambda s: s and 'Loại hợp đồng' in s)
            if contract_block:
                contract_parent = contract_block.find_next_sibling('div')
                if contract_parent:
                    contract_type = contract_parent.text.strip()

           


 
       
        job_description = None
        job_desc_div = soup.find('div', id='JobDescription')
        if job_desc_div:
            # Lấy toàn bộ HTML mô tả (nếu muốn lấy text thì dùng .get_text(separator="\n", strip=True))
            job_description = job_desc_div.decode_contents().strip()


        # Thêm vào danh sách dữ liệu
        company_data.append({
            "url": url,
            "job_title": job_title,
            "company_name": company_name,
            "address": address,
            "address_long": address_long,
            "salary": salary,
            "posted_time": posted_time,
            "expired_time": expired_time,
            "skills": skills,
            "exp": exp,
            "level": level,
            "job_type": job_type,
            "contract_type": contract_type,
            "job_description": job_description
        })

        print(f"Đã crawl: {link}")
    except Exception as e:
        print(f"Lỗi khi crawl {link}: {e}")

# Lưu thông tin vào file JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(company_data, f, ensure_ascii=False, indent=4)

print(f"Đã lưu thông tin {len(company_data)} công ty vào file {output_file}.")

driver.quit()