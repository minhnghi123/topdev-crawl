from flask import Blueprint, render_template

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/company")
def company():
    return render_template("company.html")

@main.route("/company/<string:company_name>")
def company_details(company_name):
    return render_template("company_details.html", company_name=company_name)