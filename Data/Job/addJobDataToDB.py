import sqlite3
import json

json_path = r'Data\job\job_links_full_2.json'
db_path = r'Data\crawl.db' 

with open(json_path, 'r', encoding='utf-8') as f:
    jobs = json.load(f)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def safe_str(val):
    return '' if val is None else str(val)

for job_id, job in enumerate(jobs, start=1):
    # Insert job
    cursor.execute("""
        INSERT INTO job (
            title, logo, company_name, id_company, sort_addresses, full_addresses,
            salary_min, salary_max, salary_currency, published_date, refreshed_date,
            experience, contract_type, benefits, content, responsibilities,
            requirements, benefits_original, job_url, interview, job_type, level, skills
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job.get('job_title'),
        job.get('logo'),
        job.get('company_name'),
        None,
        job.get('address'),
        job.get('address_long'),
        safe_str(job.get('salary_min')),
        safe_str(job.get('salary_max')),
        job.get('salary_currency'),
        job.get('posted_time'),
        job.get('expired_time'),
        job.get('exp'),
        job.get('contract_type'),
        job.get('BENEFIT'),
        job.get('content'),
        job.get('RESPONSIBILITIES'),
        job.get('Requirements'),
        job.get('BENEFIT'),
        job.get('url'),
        job.get('Recruitment Progress'),
        job.get('job_type'),
        job.get('level'),
        ', '.join(job.get('skills', [])) if isinstance(job.get('skills'), list) else safe_str(job.get('skills'))
    ))
    # Lấy id vừa insert (nếu có autoincrement)
    job_rowid = cursor.lastrowid

    # Xử lý skills (nếu có)
    skills = job.get('skills', [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(',') if s.strip()]
    for skill in skills:
        cursor.execute("SELECT id FROM skill WHERE name = ?", (skill,))
        result = cursor.fetchone()
        if result:
            skill_id = result[0]
        else:
            cursor.execute("INSERT INTO skill (name) VALUES (?)", (skill,))
            skill_id = cursor.lastrowid
        cursor.execute("INSERT OR IGNORE INTO job_skills (job_id, skill_id) VALUES (?, ?)", (job_rowid, skill_id))

    # Xử lý level (nếu có)
    level = job.get('level')
    if level:
        cursor.execute("SELECT id FROM level WHERE name = ?", (level,))
        result = cursor.fetchone()
        if result:
            level_id = result[0]
        else:
            cursor.execute("INSERT INTO level (name) VALUES (?)", (level,))
            level_id = cursor.lastrowid
        cursor.execute("INSERT OR IGNORE INTO job_levels (job_id, level_id) VALUES (?, ?)", (job_rowid, level_id))

    # Xử lý job_type (nếu có)
    job_type = job.get('job_type')
    if job_type:
        cursor.execute("SELECT id FROM jobType WHERE name = ?", (job_type,))
        result = cursor.fetchone()
        if result:
            job_type_id = result[0]
        else:
            cursor.execute("INSERT INTO jobType (name) VALUES (?)", (job_type,))
            job_type_id = cursor.lastrowid
        cursor.execute("INSERT OR IGNORE INTO job_jobtypes (job_id, job_type_id) VALUES (?, ?)", (job_rowid, job_type_id))

conn.commit()
conn.close()
print("Đã thêm dữ liệu từ file JSON vào bảng job và các bảng liên kết.")