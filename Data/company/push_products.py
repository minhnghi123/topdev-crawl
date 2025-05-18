import sqlite3
import json


def push_products_to_db(company,company_id,cursor):
    products = company.get('products', [])
    for product in products:
        name = product.get('name', '')
        description = product.get('description', '')
        image = product.get('image', '')
        cursor.execute('''
            INSERT INTO products  (name, description, image, company_id)
            VALUES (?, ?, ?, ?)
        ''', (name, description, image,company_id))
    print('Company products  pushed to database.')
