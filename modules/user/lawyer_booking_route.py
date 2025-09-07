from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import base64
from datetime import datetime, date


mysql = None

user_lawyers_bp = Blueprint(
    "user_lawyers_bp",
    __name__,
    template_folder="templates",   
    static_folder="static",
    static_url_path="/user_static",
)


def _need_mysql():
    if mysql is None:
        raise RuntimeError(
            "mysql is not set. In app.py: "
            "from modules.user import lawyer_booking_route as lawyer_booking_routes; "
            "lawyer_booking_routes.mysql = mysql"
        )

def _b64(img_bytes):
    """Return base64 data URL for BLOB image, or None."""
    if not img_bytes:
        return None
    try:
        return "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode("utf-8")
    except Exception:
        return None


@user_lawyers_bp.route("/lawyers")
def list_lawyers():
    """Show all active lawyers as cards."""
    _need_mysql()
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
            id,
            full_name,
            law_side,
            lawyer_note,
            avb_date,
            avb_time,
            lawyer_img,
            status,
            email,
            phone,
            address,
            nic,
            register_no
        FROM lawyer_user
        WHERE status = 1
        ORDER BY full_name ASC
    """)
    rows = cur.fetchall()
    cur.close()

    lawyers = []
    for r in rows:
        lawyers.append({
            "id": r[0],
            "full_name": r[1],
            "law_side": r[2],
            "lawyer_note": r[3],
            "avb_date": r[4],
            "avb_time": r[5],
            "photo": _b64(r[6]),
            "status": r[7],
            "email": r[8],
            "phone": r[9],
            "address": r[10],
            "nic": r[11],
            "register_no": r[12],
        })
    # NOTE: no "user/" prefix here:
    return render_template("lawyer_list.html", lawyers=lawyers)


@user_lawyers_bp.route("/lawyers/<int:lawyer_id>")
def lawyer_detail(lawyer_id: int):
    """Single lawyer profile + booking form."""
    _need_mysql()
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
            id,
            full_name,
            email,
            phone,
            address,
            nic,
            register_no,
            law_side,
            lawyer_note,
            avb_date,
            avb_time,
            lawyer_img,
            status
        FROM lawyer_user
        WHERE id=%s AND status=1
        LIMIT 1
    """, (lawyer_id,))
    r = cur.fetchone()
    cur.close()

    if not r:
        flash("Lawyer not found or inactive.", "warning")
        return redirect(url_for("user_lawyers_bp.list_lawyers"))

    lawyer = {
        "id": r[0],
        "full_name": r[1],
        "email": r[2],
        "phone": r[3],
        "address": r[4],
        "nic": r[5],
        "register_no": r[6],
        "law_side": r[7],
        "lawyer_note": r[8],
        "avb_date": r[9],
        "avb_time": r[10],
        "photo": _b64(r[11]),
        "status": r[12],
    }
    return render_template("lawyer_detail.html", lawyer=lawyer)


@user_lawyers_bp.route("/book", methods=["POST"])
def book_appointment():
    """Create an appointment (prevents double-booking per lawyer/date/time)."""
    _need_mysql()
    cur = None
    try:
        lawyer_id = int(request.form.get("lawyer_id") or 0)
        user_name = (request.form.get("user_name") or "").strip()
        user_email = (request.form.get("user_email") or "").strip()
        user_phone = (request.form.get("user_phone") or "").strip()
        appt_date_str = (request.form.get("appt_date") or "").strip()
        appt_time_str = (request.form.get("appt_time") or "").strip()
        notes = (request.form.get("notes") or "").strip()

        if not (lawyer_id and user_name and user_email and user_phone and appt_date_str and appt_time_str):
            flash("Please fill all required fields.", "error")
            return redirect(request.referrer or url_for("user_lawyers_bp.list_lawyers"))

        # Validate date/time
        try:
            appt_date = datetime.strptime(appt_date_str, "%Y-%m-%d").date()
            appt_time = datetime.strptime(appt_time_str, "%H:%M").time()
            if appt_date < date.today():
                flash("Appointment date cannot be in the past.", "error")
                return redirect(url_for("user_lawyers_bp.lawyer_detail", lawyer_id=lawyer_id))
        except ValueError:
            flash("Invalid date/time format.", "error")
            return redirect(url_for("user_lawyers_bp.lawyer_detail", lawyer_id=lawyer_id))

        user_id = session.get("user_id")  # optional

        cur = mysql.connection.cursor()

        # Check for existing booking
        cur.execute("""
            SELECT COUNT(*)
            FROM appointments
            WHERE lawyer_id=%s AND appt_date=%s AND appt_time=%s
              AND status IN ('pending','confirmed')
        """, (lawyer_id, appt_date, appt_time))
        if cur.fetchone()[0] > 0:
            cur.close()
            flash("Sorry, this time slot is already booked. Choose another.", "warning")
            return redirect(url_for("user_lawyers_bp.lawyer_detail", lawyer_id=lawyer_id))

        # Insert new appointment
        cur.execute("""
            INSERT INTO appointments
                (user_id, user_name, user_email, user_phone,
                 lawyer_id, appt_date, appt_time, notes, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'pending')
        """, (user_id, user_name, user_email, user_phone,
              lawyer_id, appt_date, appt_time, notes))
        mysql.connection.commit()
        appt_id = cur.lastrowid
        cur.close()

        flash(f"Appointment request submitted! Ref #{appt_id}.", "success")
        return redirect(url_for("user_lawyers_bp.view_appointment", appt_id=appt_id))

    except Exception:
        try:
            if cur is not None:
                mysql.connection.rollback()
        except Exception:
            pass
        flash("Error while booking. Please try again.", "error")
        return redirect(request.referrer or url_for("user_lawyers_bp.list_lawyers"))


@user_lawyers_bp.route("/appointments/<int:appt_id>")
def view_appointment(appt_id: int):
    """Simple confirmation page."""
    _need_mysql()
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
            a.id,
            a.user_name,
            a.user_email,
            a.user_phone,
            a.appt_date,
            a.appt_time,
            a.status,
            a.notes,
            l.full_name,
            l.law_side
        FROM appointments a
        JOIN lawyer_user l ON l.id = a.lawyer_id
        WHERE a.id=%s
        LIMIT 1
    """, (appt_id,))
    r = cur.fetchone()
    cur.close()

    if not r:
        flash("Appointment not found.", "warning")
        return redirect(url_for("user_lawyers_bp.list_lawyers"))

    appt = {
        "id": r[0],
        "user_name": r[1],
        "user_email": r[2],
        "user_phone": r[3],
        "appt_date": r[4],
        "appt_time": r[5],
        "status": r[6],
        "notes": r[7],
        "lawyer_name": r[8],
        "law_side": r[9],
    }
    return render_template("appointment_view.html", appt=appt)
