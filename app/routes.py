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

@main.route("/company/<string:company_id>")
def company_details(company_id):
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'company', 'companyDetails.json')
    json_company = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'company', 'companyData.json')
    with open(json_path, encoding='utf-8') as f: 
        companiesDetails = json.load(f) ; 
    with open(json_company, encoding='utf-8') as f: 
        companies = json.load(f) ; 
    company_info = companiesDetails[(int)(company_id)] ; 
    # get banner and logo 
    company =companies[(int)(company_id)]
    company_info['banner'] = company['background_image']
    company_info['logo'] = company['logo']
    return render_template("company_details.html", company_info=company_info)