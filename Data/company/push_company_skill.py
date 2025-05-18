import sqlite3
import json


def push_company_skill_to_db(company,company_id,cursor):
    skills = company.get('skills', [])
    for skill in skills:
      if skill and skill.strip():
        name = skill 
        # get id in db by name
        cursor.execute('''
            SELECT id FROM skill WHERE name = ?
        ''', (name,))
        skill_id = cursor.fetchone() ;
        # Start insert to company_skills
        if skill_id:
            skill_id = skill_id[0]
            cursor.execute('''
                INSERT OR IGNORE INTO company_skills (company_id, skill_id)
                VALUES (?, ?)
            ''', (company_id, skill_id))
    print('Company company-skills  pushed to database.')
