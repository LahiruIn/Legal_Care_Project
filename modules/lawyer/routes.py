import base64, re
from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect,
    session, url_for, flash
)
from flask_bcrypt import Bcrypt
from config.db_config import init_db
from datetime import datetime



# ─────────────────────────────────────────────────────────
# Blueprint setup
# ─────────────────────────────────────────────────────────
lawyer_bp = Blueprint(
    'lawyer',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/lawyer_static'
)

bcrypt = Bcrypt()
mysql = None  # Will be initialized via app context


# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "lawyer_username" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("lawyer.lawyer_login"))
        return f(*args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────
# Routes – Lawyer namespace
# ─────────────────────────────────────────────────────────

@lawyer_bp.route("/")
def home():
    return redirect(url_for("lawyer.lawyer_login"))


@lawyer_bp.route("/register", methods=["GET", "POST"])
def lawyer_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("lawyer.lawyer_register"))

        hashed = bcrypt.generate_password_hash(password).decode("utf-8")

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO lawyer_user (username, password) VALUES (%s, %s)",
                (username, hashed),
            )
            mysql.connection.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("lawyer.lawyer_login"))
        except Exception as exc:
            print("Registration error:", exc)
            flash("⚠️ Username already exists or database error.", "error")
            return redirect(url_for("lawyer.lawyer_register"))

    return render_template("register.html")


@lawyer_bp.route("/login", methods=["GET", "POST"])
def lawyer_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT id, username, password FROM lawyer_user WHERE username = %s",
            (username,),
        )
        user = cur.fetchone()

        if user:
            stored_hash = user[2]
            try:
                if stored_hash.startswith("$2b$") and bcrypt.check_password_hash(stored_hash, password):
                    session["lawyer_id"] = user[0]
                    session["lawyer_username"] = user[1]
                    flash("✅ Logged in!", "success")
                    return redirect(url_for("lawyer.lawyer_dashboard"))
                else:
                    flash("❌ Invalid username or password.", "error")
            except ValueError:
                flash("⚠️ Account password is invalid or corrupted. Please reset.", "error")
        else:
            flash("❌ Invalid username or password.", "error")

        return redirect(url_for("lawyer.lawyer_login"))

    return render_template("lawyer_login.html")


@lawyer_bp.route("/dashboard")
@login_required
def lawyer_dashboard():
    return render_template("lawyer_dashboard.html", username=session.get("lawyer_username"))



# ─────────────────────────────────────────────
# Lawyer profile (view + update) with Weekly Days + Time Notes
# ─────────────────────────────────────────────
# If already declared elsewhere, keep your originals:
lawyer_bp = globals().get("lawyer_bp") or Blueprint(
    "lawyer", __name__, template_folder="templates",
    static_folder="static", static_url_path="/lawyer_static"
)
bcrypt = globals().get("bcrypt") or Bcrypt()
mysql = globals().get("mysql")    # injected in app.py

email_re = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$", re.I)
nic_re   = re.compile(r"^(?:\d{9}[VvXx]|\d{12})$")
ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

def _need_mysql():
    if mysql is None:
        raise RuntimeError("mysql not set for lawyer routes. In app.py: lawyer_routes.mysql = mysql")

def _lawyer_login_required():
    if "lawyer_id" not in session:
        flash("Please log in as a lawyer.", "error")
        return False
    return True

def _b64(img_bytes):
    if not img_bytes:
        return None
    try:
        return "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode("utf-8")
    except Exception:
        return None

# ----- availability helpers -----
def _parse_days(s: str) -> set[str]:
    """
    Convert free text like:
      'Weekday', 'Weekend', 'Daily',
      'Monday, Tuesday, Saturday'
    into a set of day names.
    """
    out = set()
    if not s:
        return out
    t = s.lower().replace("&", " and ")
    if "weekday" in t:
        out.update(DAYS[:5])           # Mon-Fri
    if "weekend" in t:
        out.update(DAYS[5:])           # Sat-Sun
    if "daily" in t or "everyday" in t:
        out.update(DAYS)
    for d in DAYS:
        if d.lower() in t:
            out.add(d)
    return out

def _format_days(day_list: list[str]) -> str:
    """Return canonical CSV in Mon→Sun order, unique."""
    s = {d for d in day_list if d in DAYS}
    return ", ".join([d for d in DAYS if d in s])

@lawyer_bp.route("/profile", methods=["GET", "POST"])
def lawyer_profile():
    _need_mysql()
    if not _lawyer_login_required():
        return redirect(url_for("lawyer.lawyer_login"))

    lid = session["lawyer_id"]

    # ───────────── GET: show profile ─────────────
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT
              id, full_name, email, phone, address, nic, register_no,
              law_side, lawyer_note, avb_date, avb_time, lawyer_img,
              status, username
            FROM lawyer_user
            WHERE id=%s
            LIMIT 1
        """, (lid,))
        r = cur.fetchone()
        cur.close()

        if not r:
            flash("Lawyer not found.", "error")
            return redirect(url_for("lawyer.lawyer_logout"))

        me = {
            "id": r[0], "full_name": r[1], "email": r[2], "phone": r[3], "address": r[4],
            "nic": r[5], "register_no": r[6], "law_side": r[7], "lawyer_note": r[8],
            # parse free text days -> checkbox set; keep time text as-is
            "days": _parse_days(r[9] or ""),
            "avb_time_text": (r[10] or ""),
            "photo": _b64(r[11]), "status": r[12], "username": r[13],
        }
        return render_template("lawyer_profile.html", me=me, DAYS=DAYS)

    # ───────────── POST: update profile ─────────────
    full_name   = (request.form.get("full_name") or "").strip()
    email       = (request.form.get("email") or "").strip().lower()
    phone       = (request.form.get("phone") or "").strip()
    address     = (request.form.get("address") or "").strip()
    nic         = (request.form.get("nic") or "").strip()
    register_no = (request.form.get("register_no") or "").strip()
    law_side    = (request.form.get("law_side") or "").strip()
    lawyer_note = (request.form.get("lawyer_note") or "").strip()
    # NEW: weekly days + time notes
    days_sel    = request.form.getlist("days")  # multiple checkboxes
    avb_time_txt= (request.form.get("avb_time_text") or "").strip()
    username    = (request.form.get("username") or "").strip()
    is_active   = 1 if request.form.get("status") == "on" else 0

    new_password = request.form.get("new_password") or ""
    confirm_pw   = request.form.get("confirm_password") or ""

    # Validation
    if not all([full_name, email, phone, address, nic, register_no, law_side, username]):
        flash("Please fill all required fields.", "error")
        return redirect(url_for("lawyer.lawyer_profile"))
    if not email_re.match(email):
        flash("Invalid email address.", "error")
        return redirect(url_for("lawyer.lawyer_profile"))
    if not nic_re.match(nic):
        flash("Invalid NIC format.", "error")
        return redirect(url_for("lawyer.lawyer_profile"))
    if not days_sel:
        flash("Please select at least one available day.", "error")
        return redirect(url_for("lawyer.lawyer_profile"))
    if not avb_time_txt:
        flash("Please enter your availability time/notes.", "error")
        return redirect(url_for("lawyer.lawyer_profile"))

    # Unique email/username (excluding self)
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id FROM lawyer_user
        WHERE (LOWER(email)=LOWER(%s) OR LOWER(username)=LOWER(%s)) AND id<>%s
        LIMIT 1
    """, (email, username, lid))
    if cur.fetchone():
        cur.close()
        flash("Email or username already in use.", "error")
        return redirect(url_for("lawyer.lawyer_profile"))

    # Image
    img_file = request.files.get("lawyer_img")
    remove_photo = request.form.get("remove_photo") == "on"
    img_bytes = None
    if img_file and img_file.filename:
        ext = img_file.filename.rsplit(".", 1)[-1].lower() if "." in img_file.filename else ""
        if ext not in ALLOWED_IMAGE_EXT:
            cur.close()
            flash("Invalid image type. Use PNG/JPG/GIF/WEBP.", "error")
            return redirect(url_for("lawyer.lawyer_profile"))
        img_bytes = img_file.read()

    # Password change (optional)
    set_password = None
    if new_password or confirm_pw:
        if len(new_password) < 6:
            cur.close()
            flash("New password must be at least 6 characters.", "error")
            return redirect(url_for("lawyer.lawyer_profile"))
        if new_password != confirm_pw:
            cur.close()
            flash("Password confirmation does not match.", "error")
            return redirect(url_for("lawyer.lawyer_profile"))
        set_password = bcrypt.generate_password_hash(new_password).decode("utf-8")

    # Canonical CSV days string in order
    avb_date_csv = _format_days(days_sel)

    # Build dynamic UPDATE
    fields = [
        ("full_name", full_name),
        ("email", email),
        ("phone", phone),
        ("address", address),
        ("nic", nic),
        ("register_no", register_no),
        ("law_side", law_side),
        ("lawyer_note", lawyer_note),
        ("avb_date", avb_date_csv),      # store CSV of days
        ("avb_time", avb_time_txt),      # store free-text time/notes
        ("status", is_active),
        ("username", username),
    ]
    if img_bytes is not None:
        fields.append(("lawyer_img", img_bytes))
    elif remove_photo:
        fields.append(("lawyer_img", None))
    if set_password:
        fields.append(("password", set_password))

    set_clause = ", ".join([f"{k}=%s" for k, _ in fields])
    params = [v for _, v in fields] + [lid]

    try:
        cur.execute(f"UPDATE lawyer_user SET {set_clause} WHERE id=%s", tuple(params))
        mysql.connection.commit()
        cur.close()
        session["lawyer_username"] = username
        flash("Profile updated successfully.", "success")
    except Exception as exc:
        mysql.connection.rollback()
        cur.close()
        print("lawyer_profile update error:", exc)
        flash("Database error while saving profile.", "error")

    return redirect(url_for("lawyer.lawyer_profile"))



@lawyer_bp.route("/logout")
def lawyer_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("lawyer_login.html"))
