from flask import Blueprint, render_template, request, jsonify
import json
import os

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/company")
def company():
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'company', 'companyData.json')
    with open(json_path, encoding='utf-8') as f:
        companies = json.load(f)
    return render_template("company.html", companies=companies)

@main.route("/company/<string:company_name>")
def company_details(company_name):
    return render_template("company_details.html", company_name=company_name)