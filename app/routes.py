from flask import Blueprint, render_template

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("index.html")
@main.route("/search")
def search():
    return render_template("search.html")
@main.route("/thongke")
def thongke():
    return render_template("thongke.html")