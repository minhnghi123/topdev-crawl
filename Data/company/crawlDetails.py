import requests
from bs4 import BeautifulSoup
import json
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_company_detail(url):
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            print(f"Không thể truy cập {url}")
            return None

        soup = BeautifulSoup(res.text, 'html.parser')

        company_name = soup.select_one("h1").get_text(strip=True) if soup.select_one("h1") else "Unknown"

        slogan = soup.select_one("#common-information p")
        slogan = slogan.get_text(strip=True) if slogan else ""

        # --- Giới thiệu về công ty ---
        about_section = soup.select_one("#company-profile .prose")
        about_text = about_section.get_text("\n", strip=True) if about_section else ""
        about_html = str(about_section) if about_section else ""
        about_images = []

        if about_section:
            about_images = [img["src"].strip() for img in about_section.find_all("img") if img.has_attr("src")]

        # --- Website công ty ---
        # Cố gắng tìm đúng website chính thức của công ty
        website = ""
        website_tag = soup.select_one("div.mt-4 a[href^='http']")
        if website_tag:
            website = website_tag["href"].strip()

        # --- Địa chỉ ---
        address_tag = soup.select_one("div.mt-4 p.flex-1")
        address = address_tag.get_text(strip=True) if address_tag else ""

        # --- Kỹ năng công nghệ ---
        skills = [tag.get_text(strip=True) for tag in soup.select("div.mt-4 ul li span")]

        # --- Lĩnh vực ---
        field = soup.find("h3", string="Lĩnh vực")
        field_text = field.find_next("p").get_text(strip=True) if field else ""

        # --- Quy mô ---
        size = soup.find("h3", string="Quy mô công ty")
        size_text = size.find_next("p").get_text(strip=True) if size else ""

                # --- Vị trí tuyển dụng ---
        jobs = []
        job_section = soup.select_one("section#opening-jobs")
        if job_section:
            job_items = job_section.select("ul > li")
            for item in job_items:
                title_tag = item.select_one("h3 a")
                title = title_tag.get_text(strip=True) if title_tag else ""
                job_url = "https://topdev.vn" + title_tag["href"] if title_tag and title_tag.has_attr("href") else ""

                # Công ty
                company_tag = item.select_one("div.line-clamp-1 a.text-gray-400")
                company_name = company_tag.get_text(strip=True) if company_tag else ""

                # Địa điểm và hình thức làm việc
                location_tag = item.select_one("div.text-gray-400")
                location = location_tag.get_text(strip=True) if location_tag else ""

                # Kỹ năng
                skill_tags = item.select("div.line-clamp-1 span a span")
                skills = [tag.get_text(strip=True) for tag in skill_tags]

                # Thời gian đăng
                posted_time = item.select_one("p.text-sm.text-gray-400")
                posted = posted_time.get_text(strip=True) if posted_time else ""

                jobs.append({
                    "title": title,
                    "url": job_url,
                    "company": company_name,
                    "location": location,
                    "skills": skills,
                    "posted": posted
                })

        # Thêm vào dict kết quả
        return {
            "name": company_name,
            "slogan": slogan,
            "about_text": about_text,
            "about_html": about_html,
            "about_images": about_images,
            "website": website,
            "address": address,
            "skills": skills,
            "field": field_text,
            "company_size": size_text,
            "url": url,
            "jobs": jobs
        }


    except Exception as e:
        print(f"Lỗi khi crawl {url}: {e}")
        return None ,
def crawl_company_details():
    with open("companyData.json", "r", encoding="utf-8") as f:
        companies = json.load(f)

    detailed_companies = []

    for idx, company in enumerate(companies, 1):
        print(f"({idx}/{len(companies)}) Đang crawl: {company['name']} - {company['link']}")
        detail = get_company_detail(company['link'])
        if detail:
            detailed_companies.append(detail)
        time.sleep(1.5)  # tránh bị block

    # Lưu vào file JSON
    with open("companyDetails.json", "w", encoding="utf-8") as f:
        json.dump(detailed_companies, f, ensure_ascii=False, indent=4)

    print(f"\n Dã lưu {len(detailed_companies)} công ty chi tiết vào companyDetails.json")


if __name__ == "__main__":
    crawl_company_details()
