from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from markupsafe import Markup
from functools import wraps
from MySQLdb.cursors import DictCursor
import base64
from contextlib import closing

# ──────── Blueprint Setup ────────
lawyer_mgmt_bp = Blueprint(
    "lawyer_mgmt",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/admin_static"
)

# Initialize extensions (will be set by main app)
bcrypt = None
mysql = None

# ──────── Template Filters ────────
@lawyer_mgmt_bp.app_template_filter("b64encode")
def b64encode_filter(data):
    return Markup(base64.b64encode(data).decode("utf-8")) if data else ""

# ──────── Decorators ────────
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("admin.admin_login"))
        return f(*args, **kwargs)
    return wrapper

# ──────── Helper Functions ────────
def render_lawyer_template(template, **kwargs):
    kwargs.update({
        'username': session.get('username', 'Admin'),
        'active_page': 'lawyers'
    })
    return render_template(template, **kwargs)

def get_db_connection():
    if not mysql or not hasattr(mysql, 'connection'):
        raise RuntimeError("Database connection not initialized")
    return mysql.connection

# Routes 
@lawyer_mgmt_bp.route("/dashboard/lawyers")
@login_required
def manage_lawyers():
    try:
        with closing(get_db_connection().cursor(DictCursor)) as cur:
            cur.execute("""
                SELECT id, full_name, email, phone, law_side, register_no, 
                       lawyer_img, status
                FROM lawyer_user
                ORDER BY full_name
            """)
            lawyers = cur.fetchall()
        return render_lawyer_template("dashboard_lawyers.html", lawyers=lawyers)
    except Exception as e:
        current_app.logger.error(f"Error loading lawyers: {str(e)}", exc_info=True)
        flash("Error loading lawyers. Showing empty list.", "error")
        return render_lawyer_template("dashboard_lawyers.html", lawyers=[])

@lawyer_mgmt_bp.route("/dashboard/lawyers/view/<int:id>")
@login_required
def view_lawyer(id):
    try:
        with closing(mysql.connection.cursor(DictCursor)) as cur:
            cur.execute("SELECT * FROM lawyer_user WHERE id = %s", (id,))
            lawyer = cur.fetchone()

        if not lawyer:
            return "<h1>Lawyer not found in database.</h1>"

        # ⚠️ Temporarily remove splitting to isolate error
        # lawyer['avb_days'] = lawyer['avb_date'].split(', ') if lawyer.get('avb_date') else []

        # ✅ Force error to show up in browser
        return render_template(
            "view_lawyer.html",
            lawyer=lawyer,
            username=session.get('username', 'Admin'),
            active_page='lawyers'
        )

    except Exception as e:
        # 🚨 Show full error directly in browser
        return f"<h1>ERROR</h1><pre>{e}</pre>", 500


@lawyer_mgmt_bp.route("/dashboard/lawyers/add", methods=["GET", "POST"])
@login_required
def add_lawyer():
    if request.method == "POST":
        try:
            file = request.files.get("lawyer_img")
            lawyer_img = file.read() if file and file.filename else None

            # Process availability
            day_type = request.form.getlist("day_type[]")
            avb_days = []

            if "weekdays" in day_type:
                avb_days.extend(request.form.getlist("weekday_days[]"))
            if "weekend" in day_type:
                avb_days.extend(request.form.getlist("weekend_days[]"))

            # ✅ Fix: handle both weekday and weekend times
            weekday_time = request.form.get("weekday_time") if "weekdays" in day_type else None
            weekend_time = request.form.get("weekend_time") if "weekend" in day_type else None

            if weekday_time and weekend_time:
                avb_time = f"Weekday: {weekday_time}, Weekend: {weekend_time}"
            elif weekday_time:
                avb_time = f"Weekday: {weekday_time}"
            elif weekend_time:
                avb_time = f"Weekend: {weekend_time}"
            else:
                avb_time = None

            data = {
                "full_name": request.form.get("full_name"),
                "email": request.form.get("email"),
                "phone": request.form.get("phone"),
                "address": request.form.get("address"),
                "nic": request.form.get("nic"),
                "register_no": request.form.get("register_no"),
                "law_side": request.form.get("law_side"),
                "lawyer_note": request.form.get("lawyer_note"),
                "avb_date": ", ".join(avb_days) if avb_days else None,
                "avb_time": avb_time,
                "username": request.form.get("username"),
                "password": bcrypt.generate_password_hash(request.form.get("password")).decode("utf-8"),
                "lawyer_img": lawyer_img,
                "status": 1 if request.form.get("status") == "on" else 0
            }

            with closing(get_db_connection().cursor()) as cur:
                cur.execute("""
                    INSERT INTO lawyer_user (
                        full_name, email, phone, address, nic, register_no, law_side,
                        lawyer_note, avb_date, avb_time, username, password, lawyer_img, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, tuple(data.values()))
                get_db_connection().commit()

            flash("Lawyer added successfully.", "success")
            return redirect(url_for("lawyer_mgmt.manage_lawyers"))

        except Exception as e:
            get_db_connection().rollback()
            current_app.logger.error(f"Error adding lawyer: {str(e)}", exc_info=True)
            flash(f"Error adding lawyer: {str(e)}", "error")
            return redirect(url_for("lawyer_mgmt.add_lawyer"))

    return render_lawyer_template("add_lawyer.html")

@lawyer_mgmt_bp.route("/dashboard/lawyers/update/<int:id>", methods=["GET", "POST"])
@login_required
def update_lawyer(id):
    # ──────────────────────────────────────────────────────────────
    # POST  ➜  update the record
    # ──────────────────────────────────────────────────────────────
    if request.method == "POST":
        try:
            # ── 1. Handle optional new photo
            file = request.files.get("lawyer_img")
            lawyer_img = file.read() if file and file.filename else None

            # ── 2. Build availability days list
            day_type   = request.form.getlist("day_type[]")          # ["weekdays", "weekend"]
            avb_days   = []
            if "weekdays" in day_type:
                avb_days.extend(request.form.getlist("weekday_days[]"))
            if "weekend"  in day_type:
                avb_days.extend(request.form.getlist("weekend_days[]"))

            # ── 3. Merge weekday/weekend times into one string column
            weekday_time = request.form.get("weekday_time") if "weekdays" in day_type else None
            weekend_time = request.form.get("weekend_time") if "weekend"  in day_type else None

            if   weekday_time and weekend_time:
                avb_time = f"Weekday: {weekday_time}, Weekend: {weekend_time}"
            elif weekday_time:
                avb_time = f"Weekday: {weekday_time}"
            elif weekend_time:
                avb_time = f"Weekend: {weekend_time}"
            else:
                avb_time = None

            # ── 4. Collect the rest of the fields
            data = {
                "full_name"   : request.form.get("full_name"),
                "email"       : request.form.get("email"),
                "phone"       : request.form.get("phone"),
                "address"     : request.form.get("address"),
                "nic"         : request.form.get("nic"),
                "register_no" : request.form.get("register_no"),
                "law_side"    : request.form.get("law_side"),
                "lawyer_note" : request.form.get("lawyer_note"),
                "avb_date"    : ", ".join(avb_days) if avb_days else None,
                "avb_time"    : avb_time,
                "username"    : request.form.get("username"),
                "status"      : 1 if request.form.get("status") == "on" else 0
            }

            # ── 5. Update DB
            with closing(get_db_connection().cursor()) as cur:
                if lawyer_img:  # new photo supplied
                    cur.execute(
                        """
                        UPDATE lawyer_user SET
                            full_name   = %s,
                            email       = %s,
                            phone       = %s,
                            address     = %s,
                            nic         = %s,
                            register_no = %s,
                            law_side    = %s,
                            lawyer_note = %s,
                            avb_date    = %s,
                            avb_time    = %s,
                            username    = %s,
                            status      = %s,
                            lawyer_img  = %s
                        WHERE id = %s
                        """,
                        (*data.values(), lawyer_img, id)
                    )
                else:          # keep existing photo
                    cur.execute(
                        """
                        UPDATE lawyer_user SET
                            full_name   = %s,
                            email       = %s,
                            phone       = %s,
                            address     = %s,
                            nic         = %s,
                            register_no = %s,
                            law_side    = %s,
                            lawyer_note = %s,
                            avb_date    = %s,
                            avb_time    = %s,
                            username    = %s,
                            status      = %s
                        WHERE id = %s
                        """,
                        (*data.values(), id)
                    )
                get_db_connection().commit()

            flash("Lawyer updated successfully.", "success")
            return redirect(url_for("lawyer_mgmt.manage_lawyers"))

        except Exception as e:
            get_db_connection().rollback()
            current_app.logger.error(f"Error updating lawyer: {str(e)}", exc_info=True)
            flash(f"Error updating lawyer: {str(e)}", "error")
            return redirect(url_for("lawyer_mgmt.update_lawyer", id=id))

    # ──────────────────────────────────────────────────────────────
    # GET   ➜  load form with existing data
    # ──────────────────────────────────────────────────────────────
    try:
        with closing(get_db_connection().cursor(DictCursor)) as cur:
            cur.execute("SELECT * FROM lawyer_user WHERE id = %s", (id,))
            lawyer = cur.fetchone()

            if not lawyer:
                flash("Lawyer not found.", "error")
                return redirect(url_for("lawyer_mgmt.manage_lawyers"))

            # Split comma‑separated day list → list
            lawyer["avb_days"] = lawyer["avb_date"].split(", ") if lawyer.get("avb_date") else []

            # Split combined time string → weekday_time / weekend_time
            lawyer["weekday_time"] = None
            lawyer["weekend_time"] = None
            if lawyer.get("avb_time"):
                for part in [p.strip() for p in lawyer["avb_time"].split(",")]:
                    if part.startswith("Weekday:"):
                        lawyer["weekday_time"] = part.replace("Weekday:", "").strip()
                    elif part.startswith("Weekend:"):
                        lawyer["weekend_time"] = part.replace("Weekend:", "").strip()

            return render_lawyer_template("update_lawyer.html", lawyer=lawyer)

    except Exception as e:
        current_app.logger.error(f"Error retrieving lawyer: {str(e)}", exc_info=True)
        flash(f"Error retrieving lawyer: {str(e)}", "error")
        return redirect(url_for("lawyer_mgmt.manage_lawyers"))


@lawyer_mgmt_bp.route("/dashboard/lawyers/delete/<int:id>", methods=["POST"])
@login_required
def delete_lawyer(id):
    try:
        with closing(get_db_connection().cursor()) as cur:
            cur.execute("DELETE FROM lawyer_user WHERE id = %s", (id,))
            get_db_connection().commit()
        flash("Lawyer deleted successfully.", "success")
    except Exception as e:
        get_db_connection().rollback()
        current_app.logger.error(f"Error deleting lawyer: {str(e)}", exc_info=True)
        flash(f"Error deleting lawyer: {str(e)}", "error")
    return redirect(url_for("lawyer_mgmt.manage_lawyers"))

