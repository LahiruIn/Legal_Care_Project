from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect,
    session, url_for, flash
)
from flask_bcrypt import Bcrypt
from config.db_config import init_db
import re


# Blueprint
user_bp = Blueprint(
    "user",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/user_static",
)

bcrypt = Bcrypt()
mysql = None 

# Helpers
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("user.user_login"))
        return f(*args, **kwargs)
    return wrapper

email_re = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$", re.I)
nic_re = re.compile(r"^(?:\d{9}[VvXx]|\d{12})$")  


@user_bp.route("/")
def home():
    if "user_id" in session:  # Check if the user is logged in
        return redirect(url_for("user.user_dashboard"))  # Redirect to the dashboard if logged in
    return render_template("home.html")  # Show home page if not logged in

@user_bp.route("/register", methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        nic = (request.form.get("nic") or "").strip()
        address = (request.form.get("address") or "").strip()
        password = request.form.get("password") or ""
        city = (request.form.get("city") or "").strip()
        district = (request.form.get("district") or "").strip()
        province = (request.form.get("province") or "").strip()
        interesting_law = request.form.get("interesting_law") or None

        # Basic validation
        required = [full_name, email, nic, address, password, city, district, province]
        if not all(required):
            flash("Please fill all required fields.", "error")
            return redirect(url_for("user.user_register"))
        if not email_re.match(email):
            flash("Invalid email address.", "error")
            return redirect(url_for("user.user_register"))
        if not nic_re.match(nic):
            flash("Invalid NIC format.", "error")
            return redirect(url_for("user.user_register"))
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("user.user_register"))

        hashed = bcrypt.generate_password_hash(password).decode("utf-8")

        cur = mysql.connection.cursor()
        try:
            # Check duplicates
            cur.execute(
                "SELECT id FROM users WHERE email=%s OR nic=%s LIMIT 1",
                (email, nic),
            )
            if cur.fetchone():
                flash("Email or NIC already exists.", "error")
                return redirect(url_for("user.user_register"))

            cur.execute(
                """
                INSERT INTO users
                  (full_name, email, nic, address, password, city, district, province, interesting_law)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (full_name, email, nic, address, hashed, city, district, province, interesting_law),
            )
            mysql.connection.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("user.user_login"))
        except Exception as exc:
            print("User registration error:", exc)
            mysql.connection.rollback()
            flash("Database error. Please try again.", "error")
            return redirect(url_for("user.user_register"))

    return render_template("user_register.html")

@user_bp.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if not email or not password:
            flash("Please provide email and password.", "error")
            return redirect(url_for("user.user_login"))

        try:
            with mysql.connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, full_name, email, nic, password
                    FROM users
                    WHERE LOWER(email)=LOWER(%s)
                    LIMIT 1
                    """,
                    (email,),
                )
                row = cur.fetchone()

            if row and isinstance(row[4], str) and row[4].startswith("$2b$") \
               and bcrypt.check_password_hash(row[4], password):
                session["user_id"] = row[0]
                session["user_name"] = row[1]
                session["user_email"] = row[2]
                session["user_nic"] = row[3]
                flash("✅ Logged in!", "success")
                return redirect(url_for("user.user_dashboard"))

            flash("❌ Invalid email or password.", "error")

        except Exception as exc:
            print("User login error:", exc)
            flash("Database error while logging in. Please try again.", "error")

        return redirect(url_for("user.user_login"))

    return render_template("user_login.html")


@user_bp.route('/dashboard')
@login_required
def user_dashboard():
    return render_template("user_home.html", username=session.get("user_name"))


@user_bp.route("/about")
def about():
    return render_template("about.html")  


@user_bp.route("/services")
def services():
    return render_template("service.html")  

@user_bp.route("/privacy")
def privacy_policies():
    return render_template("privacy-policies.html")  

@user_bp.route("/contact")
def contact():
    return render_template("contact.html")  


@user_bp.route("/logout")
def user_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("user.user_dashboard"))


def init_users_module(app):
    global mysql
    mysql = init_db(app)          
    bcrypt.init_app(app)
    app.register_blueprint(user_bp, url_prefix="/user")



@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def user_profile():
    user_id = session.get("user_id")

    if request.method == "GET":
        cur = mysql.connection.cursor()  # remove dictionary=True
        cur.execute("SELECT id, full_name, email, nic, address, city, district, province FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        cur.close()

        if not row:
            flash("User not found.", "error")
            return redirect(url_for("user.user_logout"))

        # Convert tuple to dict manually
        user_data = {
            "id": row[0],
            "full_name": row[1],
            "email": row[2],
            "nic": row[3],
            "address": row[4],
            "city": row[5],
            "district": row[6],
            "province": row[7]
        }

        return render_template("user_profile.html", user=user_data)

    elif request.method == "POST":
        full_name = request.form.get("full_name").strip()
        email = request.form.get("email").strip().lower()
        password = request.form.get("password").strip()
        city = request.form.get("city").strip()
        district = request.form.get("district").strip()
        province = request.form.get("province").strip()

        if not full_name or not email or not city or not district or not province:
            flash("Please fill all required fields.", "error")
            return redirect(url_for("user.user_profile"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8") if password else None

        cur = mysql.connection.cursor()
        if hashed_password:
            cur.execute("""
                UPDATE users
                SET full_name=%s, email=%s, password=%s, city=%s, district=%s, province=%s
                WHERE id=%s
            """, (full_name, email, hashed_password, city, district, province, user_id))
        else:
            cur.execute("""
                UPDATE users
                SET full_name=%s, email=%s, city=%s, district=%s, province=%s
                WHERE id=%s
            """, (full_name, email, city, district, province, user_id))

        mysql.connection.commit()
        cur.close()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("user.user_profile"))
