from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json



def load_full_page():
    url = "https://topdev.vn/nha-tuyen-dung?src=topdev.vn&medium=mainmenu"

    options = Options()
    # options.add_argument("--headless")  # Bỏ comment nếu muốn chạy ngầm
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(3)

    click_count = 0
    max_clicks = 30  # Chỉ để phòng trường hợp infinite loop, bạn có thể tăng nếu muốn crawl nhiều hơn

    while click_count < max_clicks:
        try:
            load_more = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "load_more_button"))
            )

            # Kiểm tra xem nút có còn hiển thị không
            if not load_more.is_displayed():
                print("✅ Nút đã ẩn, kết thúc.")
                break

            driver.execute_script("window.scrollTo(0, arguments[0].getBoundingClientRect().top + window.scrollY - 200);", load_more)
            time.sleep(1)

            try:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "load_more_button")))
                load_more.click()
                print(f"🔁 Đã nhấn lần {click_count + 1}: 'Hiển thị thêm nhà tuyển dụng'")
            except ElementClickInterceptedException:
                print("⚠️ Nút bị che, dùng JavaScript để click.")
                driver.execute_script("arguments[0].click();", load_more)

            click_count += 1
            time.sleep(2)

        except Exception:
            print("✅ Không còn nút hoặc không thể nhấn nữa.")
            break

    html = driver.page_source
    driver.quit()
    return html

def crawl_companies():
    html = load_full_page()
    soup = BeautifulSoup(html, 'html.parser')
    companies = []

    for frame in soup.select('.frame.style-2'):
        name_tag = frame.select_one('h6.font-size20')
        link_tag = frame.select_one('a.link')
        logo_img_tag = frame.select_one('p.small-img img')
        bg_img_tag = frame.select_one('p.big-img img')
        desc_tag = frame.select_one('p.fz13.ml20.mb-1')
        location_tag = frame.select_one('p.fz13.c--grey.ml20.mb-2')
        industry_tag = frame.select('div.wrap-between p.fz13.c--grey.ml20')
        followers_tag = frame.select_one('span.total-followed')
        jobs_tag = frame.select_one('a.c--primary')

        name = name_tag.get_text(strip=True) if name_tag else "Unknown"
        link = link_tag['href'].strip() if link_tag and link_tag.has_attr('href') else "N/A"
        logo = logo_img_tag['src'].strip() | logo_img_tag['data-src'].strip() 
        background_image = bg_img_tag['src'].strip()| bg_img_tag["data-src"].strip()
        description = desc_tag.get_text(strip=True) if desc_tag else "N/A"
        location = location_tag.get_text(strip=True) if location_tag else "N/A"
        industry = industry_tag[-1].get_text(strip=True) if industry_tag else "N/A"
        followers = followers_tag.get_text(strip=True) if followers_tag and followers_tag.text.strip() else "0"
        jobs_count = "0"
        if jobs_tag:
            jobs_text = jobs_tag.get_text(strip=True)
            jobs_count = jobs_text.split(" ")[0] if "Jobs" in jobs_text else "0"

        # Remove extra whitespace or malformed links
        if link.startswith("/"):
            link = "https://topdev.vn" + link
        link = link.replace(" ", "")

        companies.append({
            "name": name,
            "link": link,
            "logo": logo,
            "background_image": background_image,
            "description": description,
            "location": location,
            "industry": industry,
            "followers": followers,
            "jobs_count": jobs_count
        })

    with open('companyData.json', 'w', encoding='utf-8') as f:
        json.dump(companies, f, ensure_ascii=False, indent=4)

    print(f"✅ Đã lưu {len(companies)} công ty vào companyData.json")


if __name__ == "__main__":
    crawl_companies()
