from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import random
def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Chạy ẩn
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    return driver

def get_text_or_default(driver, by, selector, default=""):
    try:
        return driver.find_element(by, selector).text.strip()
    except NoSuchElementException:
        return default

def get_company_detail(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))

        soup = BeautifulSoup(driver.page_source, "html.parser")

        company_name = get_text_or_default(driver, By.TAG_NAME, "h1", "Unknown")

        # Slogan
        slogan_tag = soup.select_one("#common-information p")
        slogan = slogan_tag.get_text(strip=True) if slogan_tag else ""

        # Giới thiệu công ty
        about_section = soup.select_one("#company-profile .prose")
        about_text = about_section.get_text("\n", strip=True) if about_section else ""
        about_html = str(about_section) if about_section else ""

        # Website
        website_tag = soup.select_one("div.mt-4 a[href^='http']")
        website = website_tag["href"].strip() if website_tag else ""

        # Địa chỉ
        address_tag = soup.select_one("div.mt-4 p.flex-1")
        address = address_tag.get_text(strip=True) if address_tag else ""

        # Kỹ năng công nghệ
        skills = [tag.get_text(strip=True) for tag in soup.select("div.mt-4 ul li span")]

        # Lĩnh vực
        field_header = soup.find("h3", string="Lĩnh vực")
        field_text = field_header.find_next("p").get_text(strip=True) if field_header else ""

        # Quy mô công ty
        size_header = soup.find("h3", string="Quy mô công ty")
        size_text = size_header.find_next("p").get_text(strip=True) if size_header else ""

        # Quốc tịch công ty
        nationality = ""
        nationality_flag = ""
        nation_header = soup.find("h3", string="Quốc tịch công ty")
        if nation_header:
            nation_item = nation_header.find_next("ul").select_one("li div")
            if nation_item:
                flag_img = nation_item.select_one("img")
                flag_text = nation_item.select_one("p")
                nationality = flag_text.get_text(strip=True) if flag_text else ""
                nationality_flag = flag_img["src"].strip() if flag_img and flag_img.has_attr("src") else ""

        # Mạng xã hội
        social_links = []
        social_header = soup.find("h3", string="Mạng xã hội")
        if social_header:
            for a_tag in social_header.find_next("ul").select("a[href]"):
                link = a_tag["href"]
                platform = ""
                icon = a_tag.select_one("i")
                if icon and icon.has_attr("class"):
                    classes = icon["class"]
                    for cls in classes:
                        if "facebook" in cls:
                            platform = "Facebook"
                        elif "linkedin" in cls:
                            platform = "LinkedIn"
                        elif "twitter" in cls:
                            platform = "Twitter"
                        elif "youtube" in cls:
                            platform = "YouTube"
                        elif "github" in cls:
                            platform = "GitHub"
                        elif "globe" in cls:
                            platform = "Website"
                social_links.append({
                    "platform": platform or "Other",
                    "url": link
                })

        # Vị trí tuyển dụng
        jobs = []
        job_section = soup.select_one("section#opening-jobs")
        if job_section:
            for item in job_section.select("ul > li"):
                title_tag = item.select_one("h3 a")
                title = title_tag.get_text(strip=True) if title_tag else ""
                job_url = "https://topdev.vn" + title_tag["href"] if title_tag and title_tag.has_attr("href") else ""

                company_tag = item.select_one("div.line-clamp-1 a.text-gray-400")
                job_company = company_tag.get_text(strip=True) if company_tag else ""

                location_tag = item.select_one("div.text-gray-400")
                location = location_tag.get_text(strip=True) if location_tag else ""

                skill_tags = item.select("div.line-clamp-1 span a span")
                job_skills = [tag.get_text(strip=True) for tag in skill_tags]

                posted_tag = item.select_one("p.text-sm.text-gray-400")
                posted = posted_tag.get_text(strip=True) if posted_tag else ""

                jobs.append({
                    "title": title,
                    "url": job_url,
                    "company": job_company,
                    "location": location,
                    "skills": job_skills,
                    "posted": posted
                })

        # Sản phẩm
        products = []
        product_section = soup.select("section#product .swiper-slide")
        for item in product_section:
            name_tag = item.select_one("a.font-bold")
            name = name_tag.get_text(strip=True) if name_tag else ""
            link = name_tag["href"].strip() if name_tag and name_tag.has_attr("href") else ""

            desc_tag = item.select_one(".prose")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            img_tag = item.select_one("img")
            image = img_tag["src"].strip() if img_tag and img_tag.has_attr("src") else ""

            products.append({
                "name": name,
                "description": description,
                "link": link,
                "image": image
            })

        # Lọc ảnh trong phần giới thiệu (loại ảnh trùng với product image)
        product_images_set = set(p["image"].strip() for p in products if p.get("image"))
        about_images = []
        for img in soup.select(".swiper-slide img"):
            src = img.get("src")
            if src and src.strip() not in product_images_set:
                about_images.append(src.strip())

        return {
            "name": company_name,
            "slogan": slogan,
            "about_text": about_text,
            "about_images": about_images,
            "website": website,
            "address": address,
            "skills": skills,
            "field": field_text,
            "company_size": size_text,
            "nationality": {
                "name": nationality,
                "flag": nationality_flag
            },
            "social_links": social_links,
            "url": url,
            "jobs": jobs,
            "products": products
        }

    except Exception as e:
        print(f"Lỗi khi crawl {url}: {e}")
        return None

def crawl_company_details():
    with open("companyData.json", "r", encoding="utf-8") as f:
        companies = json.load(f)

    driver = setup_driver()
    detailed_companies = []

    for idx, company in enumerate(companies, 1):
        print(f"({idx}/{len(companies)}) Đang crawl: {company['name']} - {company['link']}")
        detail = get_company_detail(driver, company['link'])
        if detail:
            detail["logo"] =company.get("logo", "") ;
            detail["banner"]=company.get("background_image", "") ;
            detail["short_address"]= company.get("location","") ; 
            detail["industry"]= company.get("industry","") ;
            detail["followers"] = company.get("followers", 0) ; 
            detail["jobs_count"] =  company.get("jobs_count", 0) ;
            detail["section"] = company.get("section", "") ;
            detailed_companies.append(detail)
        time.sleep(random.uniform(0.5, 1.2))

    driver.quit()

    with open("companyDetails.json", "w", encoding="utf-8") as f:
        json.dump(detailed_companies, f, ensure_ascii=False, indent=4)

    print(f"\nĐã lưu {len(detailed_companies)} công ty chi tiết vào companyDetails.json")

if __name__ == "__main__":
    crawl_company_details()
