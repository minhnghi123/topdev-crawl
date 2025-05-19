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

    keyword = request.args.get("keyword", "").strip().lower()
    city = request.args.get("city", "").strip()
    district = request.args.get("district", "").strip()

    query = Company.query

    if keyword:
        query = query.filter(Company.name.ilike(f"%{keyword}%"))
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

    return render_template("job_detail.html", job=job_dict)

