import sqlite3

def convert_salary_to_int(salary_str):
    return salary_str.replace("*", "0")

def clean_salary_data(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT id, salary_min, salary_max FROM job")
    jobs = cursor.fetchall()

    for job in jobs:
        job_id, salary_min, salary_max = job

        salary_min = convert_salary_to_int(salary_min)

        salary_max = convert_salary_to_int(salary_max)


        cursor.execute("""
            UPDATE job
            SET salary_min = ?, salary_max = ?
            WHERE id = ?
        """, (salary_min, salary_max, job_id))

    conn.commit()
    conn.close()
    print("Salary data cleaned successfully!")

db_file = "D:/18052025/topdev-crawl/Data/crawl.db"
clean_salary_data(db_file)