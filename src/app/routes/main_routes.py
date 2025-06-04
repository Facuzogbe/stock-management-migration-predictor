from flask import Blueprint, render_template, request, redirect, url_for, session
from app.utils.auth_decorators import role_required


main_bp = Blueprint("main", _name_)

# Usuario de prueba
USER_DATA = {
    "Admin": {"password": "stock2025", "role": "admin"},
    "Gerente": {"password": "stock2025", "role": "gerente"},
    "Empleado": {"password": "stock2025", "role": "empleado"},
}

# 🟢 Ruta principal: login (si no estás logueado) o redirige a /home
@main_bp.route("/", methods=["GET", "POST"])
@main_bp.route("/login", methods=["GET", "POST"])  # Alias opcional para claridad
def login():
    if "username" in session:
        return redirect(url_for("main.home"))

    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USER_DATA and USER_DATA[username]["password"] == password:
            session.permanent = True  # ✅ Activa el tiempo de sesión definido en _init_.py
            session["username"] = username
            session["role"] = USER_DATA[username]["role"]
            return redirect(url_for("main.home"))
        else:
            error = "Credenciales incorrectas. Intentalo de nuevo."

    return render_template("login/login.html", error=error)

# 🔒 Ruta protegida
@main_bp.route("/home")
def home():
    if "username" not in session:
        return redirect(url_for("main.login"))
    return render_template("home.html")

# 🔚 Cierre de sesión
@main_bp.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("main.login"))