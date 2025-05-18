import requests
import json

def fetch_all_jobs():
    base_url = "https://api.topdev.vn/td/v2/jobs"
    params = {
        "fields[job]": "id,slug,title,salary,company,extra_skills,skills_str,skills_arr,skills_ids,job_types_str,job_levels_str,job_levels_arr,job_levels_ids,addresses,status_display,detail_url,job_url,salary,published,refreshed,applied,candidate,requirements_arr,packages,benefits,content,features,is_free,is_basic,is_basic_plus,is_distinction",
        "fields[company]": "slug,tagline,addresses,skills_arr,industries_arr,industries_str,image_cover,image_galleries,benefits",
        "locale": "vi_VN",
        "ordering": "jobs_new",
        "page": 1  # Bắt đầu từ trang đầu tiên
    }

    all_jobs = set()
    while True:
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break

        data = response.json()
        jobs = data.get("data", [])
        if not jobs:
            break  # Dừng nếu không còn dữ liệu

        # Thêm từng công việc vào tập hợp all_jobs
        for job in jobs:
            all_jobs.add(json.dumps(job, sort_keys=True))  # Chuyển job thành chuỗi JSON để có thể băm được

        print(f"Fetched page {params['page']} with {len(jobs)} jobs.")

        # Tăng số trang để lấy trang tiếp theo
        params["page"] += 1

    # Lưu dữ liệu vào file JSON
    with open("all_jobs.json", "w", encoding="utf-8") as f:
        json.dump([json.loads(job) for job in all_jobs], f, ensure_ascii=False, indent=4)

    print(f"Total jobs fetched: {len(all_jobs)}")

# Gọi hàm để lấy dữ liệu
fetch_all_jobs()