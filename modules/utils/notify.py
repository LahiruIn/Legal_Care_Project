from utils.emailer import send_email

def send_appt_status_notification(mysql, appt_id: int, new_status: str) -> bool:
    """
    Sends an email to the user when status is 'confirmed' or 'cancelled'.
    Returns True if an email attempt was made, False otherwise.
    """
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

      <p style="margin-top:16px;color:#475569">
        If you have questions, reply to this email or contact support.
      </p>
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

    return send_email(subject, user_email, html=html, text=text)
