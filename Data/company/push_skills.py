import sqlite3
import json

with open('companyDetails.json', 'r', encoding='utf-8') as f:
    companies = json.load(f)

conn = sqlite3.connect('../crawl.db')
cursor = conn.cursor()

for company in companies:
    tech_stack = company.get('skills',[])  ;
    for skill in tech_stack: 
        # if skill is not in the database, insert it, and not empty 
        if skill and skill.strip():
            cursor.execute('''
                INSERT OR IGNORE INTO skill (name)
                VALUES (?)
            ''', (skill,))
conn.commit()
conn.close()
print('Company details pushed to database.')
