import matplotlib
matplotlib.use("Agg")
from flask import Blueprint, render_template, request, jsonify, current_app, send_file
import json, os, re
from app.models import Company, Products, Skill, CompanySkills, Job
import re
import math
from datetime import datetime, timedelta
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import sys
sys.path.append("ml")
from ml import search

main = Blueprint("main", __name__)

@main.record_once
def on_load(state):
    app = state.app
    with app.app_context():
        search.init_vector_dbs()

def extract_logo_url(html):
    if not html or not isinstance(html, (str, bytes)):
        return None
    match = re.search(r'<img[^>]+src="([^"]+)"', html)
    if match:
        return match.group(1)
    return None

def smart_split(text):
    sentence_end = re.compile(r'(?<!\w\.\w)(?<![A-Z][a-z]\.)(?<!\d)\.(?!\d)')
    return [s.strip() + '.' for s in sentence_end.split(text) if s.strip()]

def to_relative_time(target_time, now=None):
    if now is None:
        now = datetime.now()
    if isinstance(target_time, str):
        try:
            dt = datetime.strptime(target_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return target_time
    else:
        dt = target_time

    delta = dt - now
    seconds = int(delta.total_seconds())
    abs_seconds = abs(seconds)

    if abs_seconds < 3600:
        value = abs_seconds // 60
        unit = "phút"
    elif abs_seconds < 86400:
        value = abs_seconds // 3600
        unit = "giờ"
    elif abs_seconds < 604800:
        value = abs_seconds // 86400
        unit = "ngày"
    else:
        value = abs_seconds // 604800
        unit = "tuần"

    direction = "tới" if seconds > 0 else "trước"
    if isinstance(dt, datetime):
        formatted_time = dt.strftime('%d/%m/%Y %H:%M')
    else:
        formatted_time = str(dt)
    return f"{value} {unit} {direction} - {formatted_time}"

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/company")
def company():
    per_page = 40
    page = int(request.args.get("page", 1))

    keyword = request.args.get("keyword", "").strip().lower()
    city = request.args.get("city", "").strip()
    district = request.args.get("district", "").strip()

    query = Company.query

    company_ids = None
    if keyword:
        # Sử dụng search_companies để lấy danh sách id phù hợp nhất
        company_ids = search.search_companies(keyword, top_k=200)
        if company_ids:
            query = query.filter(Company.id.in_(company_ids))
        else:
            query = query.filter(False)  # Không có kết quả

    if district:
        query = query.filter(Company.short_address.ilike(f"%{district}%"))
    elif city:
        query = query.filter(Company.short_address.ilike(f"%{city}%"))

    total_companies = query.count()
    total_pages = math.ceil(total_companies / per_page)
    paginated = query.offset((page - 1) * per_page).limit(per_page).all()

    #  Quét full danh sách để tách thành phố & quận
    all_companies = Company.query.all()
    city_map = {}  # {"Hồ Chí Minh": ["Quận 1", "Quận 3", ...], ...}

    for company in all_companies:
        if not company.short_address:
            continue
        parts = [p.strip() for p in company.short_address.split(",")]
        if len(parts) >= 2:
            district_name = parts[0]
            city_name = parts[-1]
            if city_name not in city_map:
                city_map[city_name] = set()
            city_map[city_name].add(district_name)

    # Convert sets to sorted lists
    city_map = {city: sorted(list(districts)) for city, districts in city_map.items()}

    return render_template(
        "company.html",
        companies=paginated,
        page=page,
        total_pages=total_pages,
        keyword=keyword,
        city=city,
        district=district,
        city_map=city_map,
    )


@main.route("/company/<int:company_id>")
def company_details(company_id):
    company_info = Company.query.get_or_404(company_id)
    company_info.description_paragraphs = smart_split(company_info.description)

  # lấy job của công ty
    jobs = Job.query.filter_by(id_company=company_id).all()
    jobs_list = []
    for job in jobs:
        job_dict = job.__dict__.copy()
        if isinstance(job_dict.get('skills'), str):
            job_dict['skills'] = [s.strip() for s in job_dict['skills'].split(',') if s.strip()]
        jobs_list.append(job_dict)
    # about images
    about_images = company_info.about_images.split(',') if company_info.about_images else []

    # products
    products = Products.query.filter_by(company_id=company_id).all()
     # skills
    skills = Skill.query.join(CompanySkills, CompanySkills.skill_id == Skill.id)\
        .filter(CompanySkills.company_id == company_id).all()
    company_skill_ids = {s.id for s in skills}
    # social
    social_media = company_info.Social_media.split(',') if company_info.Social_media else []

    # === Suggestions using scoring logic ===
    def extract_city(address):
        return address.split(',')[-1].strip().lower() if address else ''

    this_city = extract_city(company_info.short_address)

    # Get all other companies except current one
    all_other_companies = Company.query.filter(Company.id != company_id).all()

    # Preload all company skills in one query
    all_skills_map = {
        cs.company_id: set()
        for cs in CompanySkills.query.filter(CompanySkills.company_id != company_id).all()
    }
    for cs in CompanySkills.query.filter(CompanySkills.company_id != company_id).all():
        all_skills_map.setdefault(cs.company_id, set()).add(cs.skill_id)

    suggestions = []

    for comp in all_other_companies:
        if comp.id == company_id:
            continue  # redundant but safe

        score = 0

        # 1. Industry match
        if comp.industry == company_info.industry:
            score += 3

        # 2. Size match
        if comp.size == company_info.size:
            score += 2

        # 3. City match
        comp_city = extract_city(comp.short_address)
        if this_city and comp_city and this_city == comp_city:
            score += 2

        # 4. Shared skills
        shared_skills = company_skill_ids & all_skills_map.get(comp.id, set())
        score += len(shared_skills)

        if score > 0:
            suggestions.append((comp, score))

    # Sort by score descending
    sorted_suggestions = sorted(suggestions, key=lambda x: x[1], reverse=True)

    # Remove duplicates (by comp.id) and limit to 6
    seen_ids = set()
    final_suggestions = []
    for comp, _ in sorted_suggestions:
        if comp.id not in seen_ids:
            final_suggestions.append(comp)
            seen_ids.add(comp.id)
        if len(final_suggestions) >= 6:
            break
    return render_template(
        "company_details.html",
        company_info=company_info,
        about_images=about_images,
        products=products,
        skills=skills,
        social_media=social_media,
        suggestions=final_suggestions,
        jobs=jobs_list,
    )

@main.route("/jobs")
def jobs():
    per_page = 40
    page = int(request.args.get("page", 1))

    # Lấy tham số lọc từ request
    keyword = request.args.get('keyword', '').lower()
    location = request.args.get('location', '')
    level = request.args.get('level', '')
    skill = request.args.get('skill', '')
    job_type = request.args.get('type', '')
    sort = request.args.get('sort', '')  # Lấy tham số sắp xếp

    query = Job.query

    job_ids = None
    if keyword:
        # Sử dụng search_jobs để lấy danh sách id phù hợp nhất
        job_ids = search.search_jobs(keyword, top_k=200)
        if job_ids:
            query = query.filter(Job.id.in_(job_ids))
        else:
            query = query.filter(False)  # Không có kết quả

    if location:
        query = query.filter(Job.sort_addresses.ilike(f"%{location}%"))
    if level:
        query = query.filter(Job.level.ilike(f"%{level}%"))
    if skill:
        query = query.filter(Job.skills.ilike(f"%{skill}%"))
    if job_type:
        query = query.filter(Job.job_type.ilike(f"%{job_type}%"))

    total_jobs = query.count()
    total_pages = math.ceil(total_jobs / per_page)
    jobs = query.offset((page - 1) * per_page).limit(per_page).all()

    # Chuyển đổi sang dict nếu cần thiết cho template
    jobs_list = []
    for job in jobs:
        job_dict = job.__dict__.copy()
        # Nếu có trường 'skills' dạng string, chuyển thành list
        if isinstance(job_dict.get('skills'), str):
            job_dict['skills'] = [s.strip() for s in job_dict['skills'].split(',') if s.strip()]
        # Nếu chưa có logo, extract từ content (nếu có html)
        if not job_dict.get('logo') and job_dict.get('content'):
            job_dict['logo'] = extract_logo_url(job_dict['content'])
        # Xử lý salary
        salary_min = job_dict.get('salary_min')
        salary_max = job_dict.get('salary_max')
        salary_currency = job_dict.get('salary_currency')
        salary_str = None
        if salary_min and salary_max:
            salary_str = f"{salary_min} - {salary_max} {salary_currency or ''}".strip()
        elif salary_min:
            salary_str = f"Từ {salary_min} {salary_currency or ''}".strip()
        elif salary_max:
            salary_str = f"Lên tới {salary_max} {salary_currency or ''}".strip()
        else:
            salary_str = "Thương lượng"
        job_dict['salary'] = salary_str
        jobs_list.append(job_dict)

    return render_template(
        "jobs.html",
        jobs=jobs_list,
        page=page,
        total_pages=total_pages
    )

@main.route("/job/<int:job_id>")
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    job_dict = job.__dict__.copy()
    # Nếu có trường 'skills' dạng string, chuyển thành list
    if isinstance(job_dict.get('skills'), str):
        job_dict['skills'] = [s.strip() for s in job_dict['skills'].split(',') if s.strip()]
    # Nếu chưa có logo, extract từ content (nếu có html)
    if not job_dict.get('logo') and job_dict.get('content'):
        job_dict['logo'] = extract_logo_url(job_dict['content'])
    # Xử lý salary
    salary_min = job_dict.get('salary_min')
    salary_max = job_dict.get('salary_max')
    salary_currency = job_dict.get('salary_currency')
    salary_str = None
    if salary_min and salary_max:
        salary_str = f"{salary_min} - {salary_max} {salary_currency or ''}".strip()
    elif salary_min:
        salary_str = f"Từ {salary_min} {salary_currency or ''}".strip()
    elif salary_max:
        salary_str = f"Lên tới {salary_max} {salary_currency or ''}".strip()
    else:
        salary_str = "Thương lượng"
    job_dict['salary'] = salary_str
    job_dict['refreshed_date_relative'] = to_relative_time(job_dict.get('refreshed_date'))

    # Lấy thông tin công ty nếu có id_company
    company_info = None
    if job_dict.get('id_company'):
        company = Company.query.get(job_dict['id_company'])
        if company:
            company_info = {
                "name": company.name,
                "size": company.size,
                "industry": company.industry,
                "address": company.address,
                "logo": company.Logo,
                "id": company.id,
            }
    job_dict['company_info'] = company_info

    # === Recommended jobs logic ===
    def extract_city(address):
        return address.split(',')[-1].strip().lower() if address else ''

    current_skills = set([s.lower() for s in job_dict.get('skills', [])])
    current_city = extract_city(job_dict.get('sort_addresses'))
    current_exp = job_dict.get('experience', '').strip().lower()

    # Lấy tất cả job khác
    all_jobs = Job.query.filter(Job.id != job_id).all()
    suggestions = []

    for other in all_jobs:
        score = 0
        # Chuẩn hóa skills
        other_skills = set()
        if isinstance(other.skills, str):
            other_skills = set([s.strip().lower() for s in other.skills.split(',') if s.strip()])
        elif isinstance(other.skills, list):
            other_skills = set([s.strip().lower() for s in other.skills if s.strip()])
        # 1. Shared skills
        shared_skills = current_skills & other_skills
        score += len(shared_skills)
        # 2. City match
        other_city = extract_city(other.sort_addresses)
        if current_city and other_city and current_city == other_city:
            score += 2
        # 3. Experience match (năm kinh nghiệm)
        other_exp = (other.experience or '').strip().lower()
        if current_exp and other_exp and current_exp == other_exp:
            score += 1
        if score > 0:
            suggestions.append((other, score))

    # Sắp xếp theo điểm giảm dần
    sorted_suggestions = sorted(suggestions, key=lambda x: x[1], reverse=True)
    # Loại trùng id và lấy tối đa 6 job
    seen_ids = set()
    recommended_jobs_list = []
    for job_obj, _ in sorted_suggestions:
        if job_obj.id not in seen_ids:
            # Chuyển sang dict cho template
            job_obj_dict = job_obj.__dict__.copy()
            if isinstance(job_obj_dict.get('skills'), str):
                job_obj_dict['skills'] = [s.strip() for s in job_obj_dict['skills'].split(',') if s.strip()]
            if not job_obj_dict.get('logo') and job_obj_dict.get('content'):
                job_obj_dict['logo'] = extract_logo_url(job_obj_dict['content'])
            # Xử lý salary cho job gợi ý
            salary_min = job_obj_dict.get('salary_min')
            salary_max = job_obj_dict.get('salary_max')
            salary_currency = job_obj_dict.get('salary_currency')
            salary_str = None
            if salary_min and salary_max:
                salary_str = f"{salary_min} - {salary_max} {salary_currency or ''}".strip()
            elif salary_min:
                salary_str = f"Từ {salary_min} {salary_currency or ''}".strip()
            elif salary_max:
                salary_str = f"Lên tới {salary_max} {salary_currency or ''}".strip()
            else:
                salary_str = "Thương lượng"
            job_obj_dict['salary'] = salary_str
            job_obj_dict['refreshed_date_relative'] = to_relative_time(job_obj_dict.get('refreshed_date'))
            recommended_jobs_list.append(job_obj_dict)
            seen_ids.add(job_obj.id)
        if len(recommended_jobs_list) >= 6:
            break

    return render_template("job_detail.html", job=job_dict, recommended_jobs=recommended_jobs_list)

@main.route("/thongke")
def thongke():
    # Lấy tất cả jobs có lương
    jobs = Job.query.filter(
        (Job.salary_min != None) | (Job.salary_max != None)
    ).all()
    salary_data = []
    usd_to_vnd = 25000
    for job in jobs:
        min_salary = job.salary_min
        max_salary = job.salary_max
        currency = (job.salary_currency or '').strip().upper()
        # Chuyển kiểu dữ liệu nếu là str
        try:
            min_salary = float(min_salary) if min_salary is not None and min_salary != '' else None
        except Exception:
            min_salary = None
        try:
            max_salary = float(max_salary) if max_salary is not None and max_salary != '' else None
        except Exception:
            max_salary = None
        if currency == "USD":
            if min_salary: min_salary = min_salary * usd_to_vnd
            if max_salary: max_salary = max_salary * usd_to_vnd
        if not min_salary and not max_salary:
            continue
        avg_salary = None
        if min_salary and max_salary:
            avg_salary = (min_salary + max_salary) / 2
        elif min_salary:
            avg_salary = min_salary
        elif max_salary:
            avg_salary = max_salary
        if avg_salary:
            salary_data.append(avg_salary)
    total_jobs = len(salary_data)
    return render_template("thongke.html", total_jobs=total_jobs)

@main.route("/thongke/chart.png")
def thongke_chart():
    # Lấy tất cả jobs có lương
    jobs = Job.query.filter(
        (Job.salary_min != None) | (Job.salary_max != None)
    ).all()
    salary_data = []
    usd_to_vnd = 25000
    for job in jobs:
        min_salary = job.salary_min
        max_salary = job.salary_max
        currency = (job.salary_currency or '').strip().upper()
        # Chuyển kiểu dữ liệu nếu là str
        try:
            min_salary = float(min_salary) if min_salary is not None and min_salary != '' else None
        except Exception:
            min_salary = None
        try:
            max_salary = float(max_salary) if max_salary is not None and max_salary != '' else None
        except Exception:
            max_salary = None
        if currency == "USD":
            if min_salary: min_salary = min_salary * usd_to_vnd
            if max_salary: max_salary = max_salary * usd_to_vnd
        if not min_salary and not max_salary:
            continue
        avg_salary = None
        if min_salary and max_salary:
            avg_salary = (min_salary + max_salary) / 2
        elif min_salary:
            avg_salary = min_salary
        elif max_salary:
            avg_salary = max_salary
        if avg_salary:
            salary_data.append(avg_salary)
    bins = [0, 10_000_000, 20_000_000, 30_000_000, 50_000_000, 70_000_000, 100_000_000, float('inf')]
    bin_labels = [
        "<10tr", "10-20tr", "20-30tr", "30-50tr", "50-70tr", "70-100tr", ">100tr"
    ]
    bin_counts = [0] * (len(bins) - 1)
    for s in salary_data:
        for i in range(len(bins) - 1):
            if bins[i] <= s < bins[i+1]:
                bin_counts[i] += 1
                break
    plt.figure(figsize=(8,4))
    plt.bar(bin_labels, bin_counts, color="#e14c2a")
    plt.xlabel("Khoảng lương (VND)")
    plt.ylabel("Số lượng công việc")
    plt.title("Phân bố lương công việc")
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

