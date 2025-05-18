import sqlite3
import json

with open('Data/company/companyDetails.json', 'r', encoding='utf-8') as f:
    companies = json.load(f)

conn = sqlite3.connect('Data/crawl.db')
cursor = conn.cursor()

for company in companies:
    name = company.get('name', '')
    logo = company.get('logo', '')
    shortdescription = company.get('slogan', '')
    curent_job_opening = int(company.get('jobs_count', 0)) if company.get('jobs_count', '').isdigit() else 0
    industry = company.get('industry', company.get('field', ''))
    size = company.get('company_size', '')
    nationality = company.get('nationality', {}).get('name', '')
    # TODO: CHECK
    tech_stack = ', '.join(company.get('skills', []))
    website = company.get('website', '')
    social_media = ', '.join([s.get('url', '') for s in company.get('social_links', [])])
    address = company.get('address', '')
    description = company.get('about_text', '')
    banner = company.get('banner','') ; 
    short_address = company.get('short_address','') ; 
    followers = int(company.get('followers',0)) if company.get('followers','').isdigit() else 0 ;
    about_images = ', '.join([s.get('url', '') for s in company.get('about_images', [])])
    cursor.execute('''
        INSERT INTO company (Logo, name, shortdescription, curent_job_opening, industry, size, nationality, tech_stack, website, Social_media, address, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (logo, name, shortdescription, curent_job_opening, industry, size, nationality, tech_stack, website, social_media, address, description,banner, short_address, followers, about_images))

conn.commit()
conn.close()
print('Company details pushed to database.')
