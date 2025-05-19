from flask import Blueprint, render_template, request, jsonify
import json, os, re
from app.models import Company, Products, Skill, CompanySkills, Job
import re
import math
from datetime import datetime, timedelta

main = Blueprint("main", __name__)

def extract_logo_url(html):
    if not html:
        return None
    match = re.search(r'<img[^>]+src="([^"]+)"', html)
    if match:
        return match.group(1)
    return None

def smart_split(text):
    sentence_end = re.compile(r'(?<!\w\.\w)(?<![A-Z][a-z]\.)(?<!\d)\.(?!\d)')
    return [s.strip() + '.' for s in sentence_end.split(text) if s.strip()]
from datetime import datetime, timedelta

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

    # Lấy keyword và location từ URL
    keyword = request.args.get("keyword", "").strip().lower()
    location = request.args.get("location", "").strip()

    # Bắt đầu query
    query = Company.query

    # Lọc theo từ khóa tên công ty
    if keyword:
        query = query.filter(Company.name.ilike(f"%{keyword}%"))

    # Lọc theo địa điểm
    if location:
        query = query.filter(Company.address.ilike(f"%{location}%"))

    # Tổng số công ty sau lọc
    total_companies = query.count()
    total_pages = math.ceil(total_companies / per_page)

    # Phân trang
    paginated = query.offset((page - 1) * per_page).limit(per_page).all()

    return render_template(
        "company.html",
        companies=paginated,
        page=page,
        total_pages=total_pages,
        keyword=keyword,
        location=location
    )


@main.route("/company/<int:company_id>")
def company_details(company_id):
    company_info = Company.query.get_or_404(company_id)
    company_info.description_paragraphs = smart_split(company_info.description)

    # divide and convert about_images to list
    about_images = company_info.about_images.split(',') if company_info.about_images else []
    # get products by company_id
    products = Products.query.filter_by(company_id=company_id).all()
    # get all skills by company_id
    skills = Skill.query.join(CompanySkills, CompanySkills.skill_id == Skill.id).filter(CompanySkills.company_id == company_id).all()
    # convert social_media to list
    social_media = company_info.Social_media.split(',') if company_info.Social_media else [] 
    return render_template("company_details.html", company_info=company_info, about_images=about_images, products=products, skills=skills,social_media=social_media)

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

    # Xây dựng query filter
    query = Job.query

    if keyword:
        query = query.filter(
            (Job.title.ilike(f"%{keyword}%")) | (Job.company_name.ilike(f"%{keyword}%"))
        )
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

    return render_template("job_detail.html", job=job_dict)

