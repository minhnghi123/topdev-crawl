import sqlite3
import requests
from bs4 import BeautifulSoup

conn = sqlite3.connect('D:\\11052025\\topdev-crawl\\Data\\crawl.db')
cursor = conn.cursor()

def insert_data(table_name, data):
    for item in data:
        cursor.execute(f"INSERT INTO {table_name}(name) VALUES (?)", (item,))
    conn.commit()


def crawl_title_topdev():
    url = "https://topdev.vn/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(soup.prettify()[:3000]) 
    job_types = [a.text.strip() for a in soup.select('a[title="Theo loại hình"] + ul a')]
    print(job_types)
    insert_data('jobType', job_types)

    levels = [a.text.strip() for a in soup.select('a[title="Theo cấp bậc"] + ul a')]
    insert_data('level', levels)
    print(levels)
    locations = [a.text.strip() for a in soup.select('a[title="Theo địa điểm"] + ul a')]
    insert_data('location', locations)
    print(locations)
    skills = [a.text.strip() for a in soup.select('a[title="Theo kỹ năng"] + ul a')]
    insert_data('skill', skills)
    print(skills)
crawl_title_topdev()

conn.close()