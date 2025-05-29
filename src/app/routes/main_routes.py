from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("home.html")



# from flask import Blueprint

# main_bp = Blueprint("main", __name__)

# @main_bp.route("/")
# def home():
#     return "Stock Platform is running!"

# @main_bp.route("/login")
# def login():
#     return "Login page placeholder"

# @main_bp.route("/products")
# def products():
#     return "Products page placeholder"

# @main_bp.route("/predict")
# def predict():
#     return "Prediction placeholder"


