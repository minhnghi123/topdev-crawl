from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta

def parse_salary(salary):
    salary_min = None
    salary_max = None
    salary_currency = None

    if "Thương lượng" in salary:
        # Trường hợp lương thương lượng
        salary_min = None
        salary_max = None
    elif "Lên tới" in salary or "to" in salary:
        # Trường hợp lương có "Lên tới" hoặc "to"
        match = re.findall(r"([\d\.]+)", salary)
        if len(match) == 1:
            # Nếu chỉ có một số, đó là salary_max
            salary_max = int(match[0].replace(".", ""))
        elif len(match) == 2:
            # Nếu có hai số, lấy salary_min và salary_max
            salary_min = int(match[0].replace(".", ""))
            salary_max = int(match[1].replace(".", ""))
    else:
        # Trường hợp khác (không có "Thương lượng" hoặc "Lên tới")
        match = re.findall(r"([\d\.]+)", salary)
        if len(match) == 2:
            salary_min = int(match[0].replace(".", ""))
            salary_max = int(match[1].replace(".", ""))

    # Xác định đơn vị tiền tệ
    if "USD" in salary:
        salary_currency = "USD"
    elif "VND" in salary:
        salary_currency = "VND"

    return salary_min, salary_max, salary_currency

def split_job_description(job_description):
    # Định nghĩa các từ khóa section (không phân biệt hoa thường)
    keywords = [
        "trách nhiệm công việc",
        "kỹ năng & chuyên môn",
        "phúc lợi dành cho bạn",
        "quy trình phỏng vấn",
        "responsibilities",
        "requirements",
        "recruitment progress",
        "benefit"
    ]
    # Tạo regex pattern cho từng từ khóa
    pattern = re.compile(
        r"^(%s)\s*:?\s*$" % "|".join(re.escape(k) for k in keywords),
        re.IGNORECASE | re.MULTILINE
    )

    # Tìm vị trí các section
    matches = list(pattern.finditer(job_description))
    sections = {}
    if not matches:
        sections["content"] = job_description.strip()
        return sections

    # Thêm phần đầu nếu có
    if matches[0].start() > 0:
        sections["content"] = job_description[:matches[0].start()].strip()

    for i, match in enumerate(matches):
        section_name = match.group(1).strip().lower()
        section_start = match.end()
        section_end = matches[i + 1].start() if i + 1 < len(matches) else len(job_description)
        section_content = job_description[section_start:section_end].strip()
        sections[section_name] = section_content

    return sections

def parse_relative_time(text, now=None):
    if now is None:
        now = datetime.now()
    text = str(text).strip()
    match = re.match(r"(\d+)\s+(giờ|ngày|tuần)\s+(trước|tới)", text)
    if not match:
        return text  # Giữ nguyên nếu không đúng định dạng
    value, unit, direction = match.groups()
    value = int(value)
    if unit == "giờ":
        delta = timedelta(hours=value)
    elif unit == "ngày":
        delta = timedelta(days=value)
    elif unit == "tuần":
        delta = timedelta(weeks=value)
    else:
        return text
    if direction == "trước":
        dt = now - delta
    else:  # "tới"
        dt = now + delta
    return dt.isoformat(sep=" ", timespec="seconds")

def convert_salary_to_int(salary):
    if salary is None:
        return None
    if isinstance(salary, str):
        return salary.replace("*", "0")
    return salary

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
job_links_file = r"Data/job/job_links_full.json"
output_file = r"Data/job/job_links_full_2.json"

# Đọc danh sách link từ file JSON
with open(job_links_file, "r", encoding="utf-8") as f:
    job_links = json.load(f)

company_data = []
# Crawl từng link
now = datetime.now()
for link in job_links:
    if not link.startswith("https://topdev.vn/viec-lam/"):
        print(f"Link không hợp lệ: {link}")
        continue
    try:
        # Mở trang web
        url = link
        driver.get(url)
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Trích xuất thông tin từ section id="detailJobHeader"
        job_section = soup.find('section', id='detailJobHeader')

        # Tiêu đề công việc
        job_title = job_section.find('h1', class_='text-2xl font-bold text-black').text.strip() if job_section.find('h1', class_='text-2xl font-bold text-black') else None
        logo_img = job_section.find("img") if job_section else None

        img = logo_img["src"] if logo_img and "src" in logo_img.attrs else None
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
            salary_min = None
            salary_max = None
            salary_currency = None
            salary_tag = main_info.find('p', class_='text-primary')
            if salary_tag:
                salary = salary_tag.text.strip()
                salary_min, salary_max, salary_currency = parse_salary(salary)

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

        job_desc_div = soup.find('div', id='JobDescription')
        job_description_sections = {
            "content": None,
            "RESPONSIBILITIES": None,
            "Requirements": None,
            "Recruitment Progress": None,
            "BENEFIT": None
        }
        if job_desc_div:
            job_desc_text = job_desc_div.get_text(separator="\n", strip=True)
            sections = split_job_description(job_desc_text)
            print(sections)
            job_description_sections["content"] = job_desc_text
            job_description_sections["RESPONSIBILITIES"] = sections.get("responsibilities", "") + " " + sections.get("trách nhiệm công việc", "")
            job_description_sections["Requirements"] = sections.get("requirements", "") + " " +  sections.get("kỹ năng & chuyên môn", "")
            job_description_sections["Recruitment Progress"] = sections.get("recruitment progress", "") + " " +  sections.get("quy trình phỏng vấn", "")
            job_description_sections["BENEFIT"] = sections.get("benefit", "") + " " +  sections.get("phúc lợi dành cho bạn", "")

        # Thêm vào danh sách dữ liệu (áp dụng chuyển đổi)
        company_data.append({
            "url": url,
            "job_title": job_title,
            "logo": img,
            "company_name": company_name,
            "address": address,
            "skills": skills,   
            "address_long": address_long,
            "salary_min": convert_salary_to_int(salary_min),
            "salary_max": convert_salary_to_int(salary_max),
            "salary_currency": salary_currency,
            "posted_time": parse_relative_time(posted_time, now) if posted_time else None,
            "exp": exp,
            "level": level,
            "job_type": job_type,
            "contract_type": contract_type,
            "expired_time": parse_relative_time(expired_time, now) if expired_time else None,
            "content": job_description_sections.get("content", ""),
            "RESPONSIBILITIES": sections.get("responsibilities", "") + " " + sections.get("trách nhiệm công việc", ""),
            "Requirements": sections.get("requirements", "") + " " + sections.get("kỹ năng & chuyên môn", ""),
            "Recruitment Progress": sections.get("recruitment progress", "") + " " + sections.get("quy trình phỏng vấn", ""),
            "BENEFIT": sections.get("benefit", "") + " " + sections.get("phúc lợi dành cho bạn", ""),
        })
        print(f"Đã crawl: {link}")
    except Exception as e:
        print(f"Lỗi khi crawl {link}: {e}")

# Lưu thông tin vào file JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(company_data, f, ensure_ascii=False, indent=4)

print(f"Đã lưu thông tin {len(company_data)} công ty vào file {output_file}.")

driver.quit()