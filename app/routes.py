from flask import Blueprint, render_template, request, jsonify
import json, os, re

main = Blueprint("main", __name__)

def extract_logo_url(html):
    if not html:
        return None
    match = re.search(r'<img[^>]+src="([^"]+)"', html)
    if match:
        return match.group(1)
    return None

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/company")
def company():
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'company', 'companyData.json')
    with open(json_path, encoding='utf-8') as f:
        companies = json.load(f)
    return render_template("company.html", companies=companies)


@main.route("/company/<string:company_id>")
def company_details(company_id):
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'company', 'companyDetails.json')
    json_company = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'company', 'companyData.json')
    with open(json_path, encoding='utf-8') as f: 
        companiesDetails = json.load(f) ; 
    with open(json_company, encoding='utf-8') as f: 
        companies = json.load(f) ; 
    company_info = companiesDetails[(int)(company_id)] ; 
    # get banner and logo 
    company =companies[(int)(company_id)]
    company_info['banner'] = company['background_image']
    company_info['logo'] = company['logo']
    return render_template("company_details.html", company_info=company_info)
  

@main.route("/jobs")
def jobs():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'Job', 'job_data.json')
    with open(data_path, encoding='utf-8') as f:
        jobs = json.load(f)

    # Extract logo for each job
    for job in jobs:
        if not job.get('logo'):
            job['logo'] = extract_logo_url(job.get('html', ''))

    # Lấy tham số lọc từ request
    keyword = request.args.get('keyword', '').lower()
    location = request.args.get('location', '')
    level = request.args.get('level', '')
    skill = request.args.get('skill', '')
    job_type = request.args.get('type', '')

    # Hàm kiểm tra từng điều kiện lọc
    def match(job):
        job_title = (job.get('title') or '').lower()
        job_company = (job.get('company') or '').lower()
        job_location = job.get('location') or ''
        job_level = job.get('level') or ''
        job_skills = job.get('skills') or []
        job_type_val = job.get('type') or ''

        if keyword and keyword not in job_title and keyword not in job_company:
            return False
        if location and location not in job_location:
            return False
        if level and level not in job_location and level not in job_level:
            return False
        if skill and skill not in job_skills:
            return False
        if job_type and job_type not in job_type_val:
            return False
        return True

    # Lọc danh sách công việc
    filtered_jobs = [job for job in jobs if match(job)]

    return render_template("jobs.html", jobs=filtered_jobs)
@main.route("/job/<int:job_id>")
def job_detail(job_id):
    data_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'Job', 'job_data.json')
    with open(data_path, encoding='utf-8') as f:
        jobs = json.load(f)
    # Lấy job theo index
    if 0 <= job_id < len(jobs):
        job = jobs[job_id]
    else:
        return "Không tìm thấy công việc", 404
    return render_template("job_detail.html", job=job)

