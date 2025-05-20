import sqlite3

db_path = r'Data\crawl.db' 

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def safe_str(val):
    return '' if val is None else str(val)

cursor.execute("SELECT id, company_name FROM job")
jobs = cursor.fetchall()

for job_row in jobs:
    job_id, company_name = job_row
    company_id = None
    if company_name:
        cursor.execute("SELECT id FROM company WHERE name = ?", (company_name,))
        result = cursor.fetchone()
        if result:
            company_id = result[0]
        else:
            company_id = None

    cursor.execute("UPDATE job SET id_company = ? WHERE id = ?", (company_id, job_id))

    if company_id:
        cursor.execute(
            "SELECT 1 FROM job_company WHERE id_job = ? AND id_company = ?",
            (job_id, company_id)
        )
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(
                "INSERT INTO job_company (id_job, id_company) VALUES (?, ?)",
                (job_id, company_id)
            )

conn.commit()
conn.close()
print("Đã cập nhật id_company và bảng job_company từ dữ liệu trong DB.")