import sqlite3
import requests
import json

def fetch_and_insert_jobs(api_url, db_file):
    # Kết nối đến SQLite
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Gửi yêu cầu đến API
    params = {
        "fields[job]": "id,slug,title,salary,company,extra_skills,skills_str,skills_arr,skills_ids,job_types_str,job_levels_str,job_levels_arr,job_levels_ids,addresses,status_display,detail_url,job_url,salary,published,refreshed,applied,candidate,requirements_arr,packages,benefits,content,features,is_free,is_basic,is_basic_plus,is_distinction",
        "fields[company]": "slug,tagline,addresses,skills_arr,industries_arr,industries_str,image_cover,image_galleries,benefits",
        "locale": "vi_VN",
        "ordering": "jobs_new",
        "page": 1  
    }

    while True:
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            print(f"Error fetching data from API. Status code: {response.status_code}")
            break

        data = response.json()
        jobs = data.get("data", [])
        if not jobs:
            break  

        # Chèn dữ liệu vào cơ sở dữ liệu
        for job in jobs:
            # Xử lý addresses
            addresses = job.get("addresses", [])
            if isinstance(addresses, list):  # Nếu addresses là danh sách
                full_addresses = json.dumps([addr.get("full_addresses", "") for addr in addresses])
                sort_addresses = json.dumps([addr.get("sort_addresses", "") for addr in addresses])
            else:  # Nếu addresses không phải là danh sách (có thể là chuỗi hoặc None)
                full_addresses = json.dumps([addresses]) if addresses else "[]"
                sort_addresses = "[]"

            # Xử lý salary
            salary = job.get("salary", {})
            salary_min = salary.get("min", None)
            salary_max = salary.get("max", None)
            is_negotiable = salary.get("is_negotiable", False)
        
            salary_unit = job.get("salary", {}).get("unit", "") 
            if isinstance(salary_unit, dict):  
                salary_unit = json.dumps(salary_unit)

            # Thêm job vào bảng job
            cursor.execute("""
            INSERT OR IGNORE INTO job (
                id, title, company_name, full_addresses, salary_min, salary_max, salary_currency, salary_unit, 
                isNegotiableSalary, benefits, content, sort_addresses, published_date, refreshed_date, 
                responsibilities, requirements, benefits_original, job_url,logo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
            """, (
                job.get("id"),
                job.get("title", ""),
                str(job.get("company", {}).get("display_name", "")),  # Ensure company_name is a string
                json.dumps(job.get("addresses", {}).get("full_addresses", [])),  # Serialize full_addresses
                job.get("salary", {}).get("min", None),  # Salary min
                job.get("salary", {}).get("max", None),  # Salary max
                job.get("salary", {}).get("currency", ""),  # Salary currency (e.g., USD)
                salary_unit,  # Updated salary_unit
                bool(int(job.get("salary", {}).get("is_negotiable", 0))),  # Convert "0"/"1" to boolean
                json.dumps(job.get("benefits", [])),  # Serialize benefits as JSON
                job.get("content", ""),
                json.dumps(job.get("addresses", {}).get("sort_addresses", "")),  # Serialize sort_addresses
                job.get("published", {}).get("date", ""),
                job.get("refreshed", {}).get("date", ""),
                job.get("responsibilities_original", ""),
                job.get("requirements_original", ""),
                json.dumps(job.get("benefits_original", [])),  # Serialize benefits_original
                job.get("detail_url", "")
                job.get("company", {}).get("image_logo", ""),
            ))

            # Xử lý skills_str
            skills = job.get("skills_str", "").split(", ")
            for skill in skills:
                if skill:
                    cursor.execute("SELECT id FROM skill WHERE name = ?", (skill,))
                    result = cursor.fetchone()
                    if result:
                        skill_id = result[0]  # Lấy id nếu đã tồn tại
                    else:
                        # Chèn mới nếu chưa tồn tại
                        cursor.execute("INSERT INTO skill (name) VALUES (?)", (skill,))
                        skill_id = cursor.lastrowid  # Lấy id của bản ghi vừa chèn
                    # Chèn vào bảng job_skills
                    cursor.execute("INSERT OR IGNORE INTO job_skills (job_id, skill_id) VALUES (?, ?)", (job.get("id"), skill_id))

            # Xử lý job_levels_str
            levels = job.get("job_levels_str", "").split(", ")
            for level in levels:
                if level:
                    cursor.execute("SELECT id FROM level WHERE name = ?", (level,))
                    result = cursor.fetchone()
                    if result:
                        level_id = result[0]  
                    else:
                        cursor.execute("INSERT INTO level (name) VALUES (?)", (level,))
                        level_id = cursor.lastrowid  
                    cursor.execute("INSERT OR IGNORE INTO job_levels (job_id, level_id) VALUES (?, ?)", (job.get("id"), level_id))

            # Xử lý job_types_str
            job_types = job.get("job_types_str", "").split(", ")
            for job_type in job_types:
                if job_type:
                    cursor.execute("SELECT id FROM jobType WHERE name = ?", (job_type,))
                    result = cursor.fetchone()
                    if result:
                        job_type_id = result[0]  
                    else:
                        cursor.execute("INSERT INTO jobType (name) VALUES (?)", (job_type,))
                        job_type_id = cursor.lastrowid  
                    cursor.execute("INSERT OR IGNORE INTO job_jobtypes (job_id, job_type_id) VALUES (?, ?)", (job.get("id"), job_type_id))

        print(f"Fetched and inserted page {params['page']} with {len(jobs)} jobs.")
        params["page"] += 1  # Tăng số trang để lấy trang tiếp theo

    # Lưu thay đổi và đóng kết nối
    conn.commit()
    conn.close()
    print("All data fetched and inserted successfully!")

# Gọi hàm để lấy dữ liệu từ API và chèn vào cơ sở dữ liệu
api_url = "https://api.topdev.vn/td/v2/jobs"
db_file = "D:/18052025/topdev-crawl/Data/crawl.db"
fetch_and_insert_jobs(api_url, db_file)
