from flask import Blueprint, render_template, session, redirect, url_for, flash
from datetime import datetime, date, time


mysql = None

user_appt_bp = Blueprint(
    "user_appt",
    __name__,
    template_folder="templates",   
    static_folder="static",
    static_url_path="/user_static",
)

def _need_login():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return False
    return True

@user_appt_bp.route("/appointments")
def my_appointments():
    if not _need_login():
        return redirect(url_for("user.user_login"))

    uid = session["user_id"]

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT a.id, a.appt_date, a.appt_time, a.status, a.notes,
               l.full_name, l.law_side
        FROM appointments a
        JOIN lawyer_user l ON l.id = a.lawyer_id
        WHERE a.user_id = %s
        ORDER BY a.appt_date DESC, a.appt_time DESC, a.id DESC
    """, (uid,))
    rows = cur.fetchall()
    cur.close()

    appts = []
    now = datetime.now()
    for r in rows:
        appt_id, d, t, status, notes, lawyer_name, law_side = r

        derived = status
        try:
            if status in ("pending", "confirmed"):
                if isinstance(d, date) and isinstance(t, time):
                    when = datetime.combine(d, t)
                    if when < now:
                        derived = "missed"  
        except Exception:
            pass

        appts.append({
            "id": appt_id,
            "date": d, "time": t,
            "status": status,
            "derived": derived,  
            "notes": notes,
            "lawyer_name": lawyer_name,
            "law_side": law_side,
        })

    return render_template("user_appointments.html", appts=appts)
