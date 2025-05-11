import sqlite3

conn = sqlite3.connect('D:\\11052025\\topdev-crawl\\Data\\crawl.db')
cursor = conn.cursor()

# # Tạo bảng job
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS job (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     title TEXT NOT NULL,
#     name_company TEXT NOT NULL,
#     id_company INTEGER,
#     address TEXT,
#     salary TEXT,
#     date_expire TEXT,
#     experience TEXT,
#     contract_type TEXT,
#     description TEXT,
# )
# ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS company (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Logo TEXT,
    name TEXT NOT NULL,
    shortdescription TEXT,
    curent_job_opening INTEGER,          
    industry TEXT,
    size TEXT,
    nationality TEXT,
    tech_stack TEXT,
    website TEXT,
    Social_media TEXT,
    address TEXT,
    description TEXT
)
''')
conn.commit()
conn.close()