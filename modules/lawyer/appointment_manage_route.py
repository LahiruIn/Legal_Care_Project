# modules/lawyer/appointment_manage_route.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import smtplib
from email.message import EmailMessage

# mysql is injected from app.py like:
#   from modules.lawyer import appointment_manage_route as appt_routes
#   appt_routes.mysql = mysql
mysql = None

lawyer_appt_bp = Blueprint(
    "lawyer_appt",
    __name__,
    template_folder="templates",   # modules/lawyer/templates
    static_folder="static",
    static_url_path="/lawyer_static",
)

ALLOWED_APPT_STATUSES = ("pending", "confirmed", "cancelled", "done")

# ───────────────── email helpers (inline to avoid 'utils' import) ─────────────────
def _send_email(subject: str, to_addr: str, html: str = None, text: str = None) -> bool:
    cfg = current_app.config
    host = cfg.get("MAIL_HOST")
    port = int(cfg.get("MAIL_PORT", 587))
    use_tls = bool(cfg.get("MAIL_USE_TLS", True))
    username = cfg.get("MAIL_USERNAME")
    password = cfg.get("MAIL_PASSWORD")
    from_addr = cfg.get("MAIL_FROM") or username
    sender_name = cfg.get("MAIL_SENDER_NAME", "Legal Care")

    if not (host and port and username and password and from_addr and to_addr):
        current_app.logger.warning("Email not sent – mail config incomplete.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{sender_name} <{from_addr}>"
    msg["To"] = to_addr
    if html:
        msg.set_content(text or "Notification")
        msg.add_alternative(html, subtype="html")
    else:
        msg.set_content(text or "Notification")

    with smtplib.SMTP(host, port) as s:
        if use_tls:
            s.starttls()
        s.login(username, password)
        s.send_message(msg)
    return True


def _notify_user_on_status(mysql, appt_id: int, new_status: str) -> bool:
    """Send email when status is confirmed or cancelled."""
    if new_status not in ("confirmed", "cancelled"):
        return False

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
          a.id, a.user_name, a.user_email, a.appt_date, a.appt_time, a.notes,
          l.full_name AS lawyer_name, l.law_side
        FROM appointments a
        JOIN lawyer_user l ON l.id = a.lawyer_id
        WHERE a.id = %s
        LIMIT 1
    """, (appt_id,))
    r = cur.fetchone()
    cur.close()

    if not r:
        return False

    appt_id, user_name, user_email, appt_date, appt_time, notes, lawyer_name, law_side = r
    if not user_email:
        return False

    if new_status == "confirmed":
        subject = f"Your appointment #{appt_id} is confirmed"
        lead = "Your appointment has been confirmed."
        color = "#16a34a"
    else:
        subject = f"Your appointment #{appt_id} was rejected"
        lead = "Unfortunately, your appointment was rejected."
        color = "#dc2626"

    html = f"""
    <div style="font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif;color:#0f172a">
      <h2 style="margin:0 0 8px">{subject}</h2>
      <p style="margin:0 0 16px;color:{color};font-weight:600">{lead}</p>
      <table style="border-collapse:collapse;font-size:14px">
        <tr><td style="padding:4px 8px;color:#475569">Lawyer</td><td style="padding:4px 8px">{lawyer_name} ({law_side})</td></tr>
        <tr><td style="padding:4px 8px;color:#475569">Date</td><td style="padding:4px 8px">{appt_date}</td></tr>
        <tr><td style="padding:4px 8px;color:#475569">Time</td><td style="padding:4px 8px">{appt_time}</td></tr>
        <tr><td style="padding:4px 8px;color:#475569">Notes</td><td style="padding:4px 8px">{(notes or '')}</td></tr>
        <tr><td style="padding:4px 8px;color:#475569">Reference</td><td style="padding:4px 8px">#{appt_id}</td></tr>
      </table>
      <p style="margin-top:16px;color:#475569">If you have questions, reply to this email or contact support.</p>
    </div>
    """
    text = (
        f"{subject}\n\n"
        f"Lawyer: {lawyer_name} ({law_side})\n"
        f"Date: {appt_date}\n"
        f"Time: {appt_time}\n"
        f"Notes: {notes or ''}\n"
        f"Ref: #{appt_id}\n"
    )
    return _send_email(subject, user_email, html=html, text=text)

# ───────────────── helpers ─────────────────
def _need_mysql():
    if mysql is None:
        raise RuntimeError("mysql not set. In app.py: appointment_manage_route.mysql = mysql")

def _guard():
    if "lawyer_id" not in session:
        flash("Please log in as a lawyer.", "error")
        return False
    return True

# ───────────────── routes ─────────────────
@lawyer_appt_bp.route("/appointments")
def lawyer_appointments():
    _need_mysql()
    if not _guard():
        return redirect(url_for("lawyer.lawyer_login"))

    lid = session["lawyer_id"]

    status    = (request.args.get("status") or "").strip().lower()
    q         = (request.args.get("q") or "").strip().lower()
    date_from = (request.args.get("from") or "").strip()
    date_to   = (request.args.get("to") or "").strip()

    where  = ["a.lawyer_id=%s"]
    params = [lid]

    if status in ALLOWED_APPT_STATUSES:
        where.append("a.status=%s"); params.append(status)
    if q:
        like = f"%{q}%"
        where.append("(LOWER(a.user_name) LIKE %s OR LOWER(a.user_email) LIKE %s OR LOWER(a.user_phone) LIKE %s)")
        params += [like, like, like]
    if date_from:
        where.append("a.appt_date >= %s"); params.append(date_from)
    if date_to:
        where.append("a.appt_date <= %s"); params.append(date_to)

    sql = f"""
        SELECT a.id, a.user_name, a.user_email, a.user_phone,
               a.appt_date, a.appt_time, a.notes, a.status, a.created_at
        FROM appointments a
        WHERE {' AND '.join(where)}
        ORDER BY a.appt_date ASC, a.appt_time ASC, a.id ASC
    """

    cur = mysql.connection.cursor()
    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    cur.close()

    appts = [{
        "id": r[0], "user_name": r[1], "user_email": r[2], "user_phone": r[3],
        "appt_date": r[4], "appt_time": r[5], "notes": r[6], "status": r[7], "created_at": r[8],
    } for r in rows]

    return render_template(
        "lawyer_appointments.html",
        appts=appts,
        statuses=ALLOWED_APPT_STATUSES,
        filters={"status": status, "q": q, "from": date_from, "to": date_to},
    )


@lawyer_appt_bp.route("/appointments/<int:appt_id>/status", methods=["POST"])
def lawyer_update_appt_status(appt_id: int):
    _need_mysql()
    if not _guard():
        return redirect(url_for("lawyer.lawyer_login"))

    lid = session["lawyer_id"]
    new_status = (request.form.get("status") or "").strip().lower()

    if new_status not in ALLOWED_APPT_STATUSES:
        flash("Invalid status.", "error")
        return redirect(request.referrer or url_for("lawyer_appt.lawyer_appointments"))

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "UPDATE appointments SET status=%s WHERE id=%s AND lawyer_id=%s",
            (new_status, appt_id, lid)
        )
        if cur.rowcount == 0:
            flash("Appointment not found.", "warning")
        else:
            mysql.connection.commit()
            flash(f"Status updated to {new_status}.", "success")
            if new_status in ("confirmed", "cancelled"):
                _notify_user_on_status(mysql, appt_id, new_status)
    except Exception as exc:
        mysql.connection.rollback()
        print("lawyer_update_appt_status:", exc)
        flash("DB error while updating status.", "error")
    finally:
        cur.close()

    return redirect(request.referrer or url_for("lawyer_appt.lawyer_appointments"))


@lawyer_appt_bp.route("/appointments/<int:appt_id>/delete", methods=["POST"])
def lawyer_delete_appt(appt_id: int):
    _need_mysql()
    if not _guard():
        return redirect(url_for("lawyer.lawyer_login"))

    lid = session["lawyer_id"]
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM appointments WHERE id=%s AND lawyer_id=%s", (appt_id, lid))
        if cur.rowcount == 0:
            flash("Appointment not found.", "warning")
        else:
            mysql.connection.commit()
            flash("Appointment deleted.", "success")
    except Exception as exc:
        mysql.connection.rollback()
        print("lawyer_delete_appt:", exc)
        flash("DB error while deleting.", "error")
    finally:
        cur.close()

    return redirect(request.referrer or url_for("lawyer_appt.lawyer_appointments"))


def init_lawyer_appointments_module(app, mysql_instance):
    """Optional one-liner init."""
    global mysql
    mysql = mysql_instance
    app.register_blueprint(lawyer_appt_bp, url_prefix="/lawyer")
