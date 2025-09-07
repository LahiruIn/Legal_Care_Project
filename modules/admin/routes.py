import os
from uuid import uuid4
from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect,
    session, url_for, flash, jsonify, current_app
)
from flask_bcrypt import Bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename

admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/admin_static'
)

bcrypt = Bcrypt()
mysql = None  # injected in app.py: admin_routes.mysql = mysql

# Allowed statuses for appointments (keep in UI sync)
_APPT_STATUSES = ("pending", "confirmed", "cancelled", "complete")
_APPT_STATUS_SET = set(_APPT_STATUSES)

# ─────────── Helpers ───────────
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("admin.admin_login"))
        return f(*args, **kwargs)
    return wrapper

def _ensure_mysql():
    if mysql is None:
        raise RuntimeError("mysql not set for admin routes. In app.py: admin_routes.mysql = mysql")

def _wants_json():
    return (
        request.is_json
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or (request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html)
    )

def _respond_ok(msg, code=200):
    if _wants_json():
        return jsonify(ok=True, message=msg), code
    flash(msg, "success")
    return redirect(request.referrer or url_for("admin.admin_appointments"))

def _respond_err(msg, code=400):
    if _wants_json():
        return jsonify(ok=False, error=msg), code
    flash(msg, "error")
    return redirect(request.referrer or url_for("admin.admin_appointments"))

@admin_bp.app_context_processor
def inject_username():
    # Prevents UndefinedError in base templates when {{ username }} is used
    return dict(username=session.get("username"))

# ─────────── Routes: Admin Auth ───────────
@admin_bp.route("/")
def home():
    return redirect(url_for("admin.admin_login"))

@admin_bp.route("/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if not username or not password:
            flash("Username and password required.", "error")
            return redirect(url_for("admin.admin_register"))

        hashed = bcrypt.generate_password_hash(password).decode("utf-8")

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO admin_user (username, password) VALUES (%s, %s)",
                (username, hashed),
            )
            mysql.connection.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("admin.admin_login"))
        except Exception as exc:
            current_app.logger.exception("Registration error: %s", exc)
            mysql.connection.rollback()
            flash("⚠️ Username already exists or DB error.", "error")
            return redirect(url_for("admin.admin_register"))
        finally:
            cur.close()

    return render_template("register.html", active_page="register")

@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT id, username, password FROM admin_user WHERE username = %s",
            (username,),
        )
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            flash(" Logged in!", "success")
            return redirect(url_for("admin.admin_dashboard"))

        flash(" Invalid username or password.", "error")
        return redirect(url_for("admin.admin_login"))

    return render_template("login.html", active_page="login")

@admin_bp.route("/dashboard")
@login_required
def admin_dashboard():
    return render_template(
        "dashboard.html",
        username=session.get("username"),
        active_page="dashboard"
    )

@admin_bp.route("/logout")
def admin_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("admin.admin_login"))

# ─────────── Appointments ───────────
@admin_bp.route("/appointments")
@login_required
def admin_appointments():
    """
    View all appointments with optional filters:
    - status: pending/confirmed/cancelled/complete
    - q: search across user_name, user_email, lawyer name
    - from, to: date range on appt_date
    """
    _ensure_mysql()

    status = (request.args.get("status") or "").strip().lower()
    q = (request.args.get("q") or "").strip().lower()
    date_from = (request.args.get("from") or "").strip()
    date_to = (request.args.get("to") or "").strip()

    where = []
    params = []

    if status in _APPT_STATUS_SET:
        where.append("a.status=%s")
        params.append(status)

    if q:
        where.append("(LOWER(a.user_name) LIKE %s OR LOWER(a.user_email) LIKE %s OR LOWER(l.full_name) LIKE %s)")
        like = f"%{q}%"
        params.extend([like, like, like])

    if date_from:
        where.append("a.appt_date >= %s")
        params.append(date_from)
    if date_to:
        where.append("a.appt_date <= %s")
        params.append(date_to)

    sql = """
        SELECT
            a.id,
            a.user_name,
            a.user_email,
            a.user_phone,
            a.appt_date,
            a.appt_time,
            a.status,
            a.notes,
            a.created_at,
            l.full_name,
            l.law_side
        FROM appointments a
        JOIN lawyer_user l ON l.id = a.lawyer_id
    """
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY a.appt_date DESC, a.appt_time DESC, a.id DESC"

    cur = mysql.connection.cursor()
    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    cur.close()

    appts = []
    for r in rows:
        appts.append({
            "id": r[0],
            "user_name": r[1],
            "user_email": r[2],
            "user_phone": r[3],
            "appt_date": r[4],
            "appt_time": r[5],
            "status": r[6],
            "notes": r[7],
            "created_at": r[8],
            "lawyer_name": r[9],
            "law_side": r[10],
        })

    return render_template(
        "appointments.html",
        appts=appts,
        filters={"status": status, "q": q, "from": date_from, "to": date_to},
        statuses=_APPT_STATUSES,
        active_page="appointments"
    )

@admin_bp.route("/appointments/<int:appt_id>/status", methods=["POST"])
@login_required
def admin_update_appt_status(appt_id: int):
    _ensure_mysql()

    payload = request.get_json(silent=True) or request.form or {}
    new_status = (payload.get("status") or "").strip().lower()

    if new_status not in _APPT_STATUS_SET:
        return _respond_err("Invalid status.", 400)

    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE appointments SET status=%s WHERE id=%s", (new_status, appt_id))
        mysql.connection.commit()

        if cur.rowcount == 0:
            return _respond_err("Appointment not found.", 404)

        return _respond_ok(f"Status updated to {new_status}.", 200)
    except Exception as exc:
        current_app.logger.exception("Status update error: %s", exc)
        mysql.connection.rollback()
        return _respond_err("DB error while updating status.", 500)
    finally:
        cur.close()

# ─────────── Admin · Law Content (Create, List, View, Edit, Delete) ───────────
# Upload locations under the admin blueprint's static folder
UPLOAD_ROOT = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
IMG_SUBDIR = 'images'
DOC_SUBDIR = 'docs'
os.makedirs(os.path.join(UPLOAD_ROOT, IMG_SUBDIR), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_ROOT, DOC_SUBDIR), exist_ok=True)

ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_DOC_EXT   = {"pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "txt"}

def _file_ext(filename: str) -> str:
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

def _save_upload(file_storage, subdir: str, allowed_ext: set):
    """Save uploaded file into /modules/admin/static/uploads/<subdir>/... and return relative path for url_for('admin.static', filename=rel_path)."""
    if not file_storage or file_storage.filename == '':
        return None, None
    ext = _file_ext(file_storage.filename)
    if ext not in allowed_ext:
        return None, f"Invalid file type .{ext}. Allowed: {', '.join(sorted(allowed_ext))}"
    safe = secure_filename(file_storage.filename)
    unique_name = f"{uuid4().hex}_{safe}"
    abs_dir = os.path.join(UPLOAD_ROOT, subdir)
    abs_path = os.path.join(abs_dir, unique_name)
    file_storage.save(abs_path)
    rel_path = f"uploads/{subdir}/{unique_name}"   # stored in DB
    return rel_path, None

def _abs_upload_path(rel_path: str) -> str | None:
    """Convert a stored relative path (uploads/...) to an absolute path, safely."""
    if not rel_path:
        return None
    abs_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'static', rel_path))
    # prevent path traversal; ensure inside UPLOAD_ROOT
    try:
        if os.path.commonpath([abs_path, UPLOAD_ROOT]) != UPLOAD_ROOT:
            return None
    except ValueError:
        # Different drives on Windows, bail out safely
        return None
    return abs_path

def _delete_file(rel_path: str):
    """Delete a previously saved upload if it exists."""
    ap = _abs_upload_path(rel_path)
    if ap and os.path.exists(ap):
        try:
            os.remove(ap)
        except Exception:
            pass

# ------------- Create -------------
@admin_bp.route("/content/new", methods=["GET", "POST"])
@login_required
def admin_content_new():
    _ensure_mysql()

    if request.method == "POST":
        kind = (request.form.get("kind") or "").strip().lower()
        title = (request.form.get("title") or "").strip()
        summary = (request.form.get("summary") or "").strip()
        body = (request.form.get("body") or "").strip()
        external_link = (request.form.get("external_link") or "").strip()
        publish_now = request.form.get("publish_now") == "on"

        if kind not in ("update", "document", "news", "image"):
            flash("Please select a valid type.", "error")
            return redirect(url_for("admin.admin_content_new"))
        if not title:
            flash("Title is required.", "error")
            return redirect(url_for("admin.admin_content_new"))

        img_file = request.files.get("image_file")
        doc_file = request.files.get("doc_file")

        image_path, img_err = _save_upload(img_file, IMG_SUBDIR, ALLOWED_IMAGE_EXT)
        if img_err:
            flash(img_err, "error")
            return redirect(url_for("admin.admin_content_new"))

        doc_path, doc_err = _save_upload(doc_file, DOC_SUBDIR, ALLOWED_DOC_EXT)
        if doc_err:
            flash(doc_err, "error")
            return redirect(url_for("admin.admin_content_new"))

        if kind == "image" and not image_path:
            flash("Please upload an image for Image posts.", "error")
            return redirect(url_for("admin.admin_content_new"))
        if kind == "document" and not doc_path:
            flash("Please upload a document for Document posts.", "error")
            return redirect(url_for("admin.admin_content_new"))

        published_at = datetime.now() if publish_now else None
        author_admin_id = session.get("user_id")

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO law_content
                  (kind, title, summary, body, image_path, doc_path, external_link, author_admin_id, published_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (kind, title, summary or None, body or None, image_path, doc_path,
                  external_link or None, author_admin_id, published_at))
            mysql.connection.commit()
            flash("Content created.", "success")
            return redirect(url_for("admin.admin_content_list"))
        except Exception as exc:
            mysql.connection.rollback()
            current_app.logger.exception("admin_content_new error: %s", exc)
            flash("DB error while creating content.", "error")
            return redirect(url_for("admin.admin_content_new"))
        finally:
            cur.close()

    return render_template("content_new.html", active_page="content_new")

# ------------- List -------------
@admin_bp.route("/content")
@login_required
def admin_content_list():
    _ensure_mysql()

    kind = (request.args.get("kind") or "").strip().lower()
    q = (request.args.get("q") or "").strip().lower()

    where = []
    params = []

    if kind in ("update", "document", "news", "image"):
        where.append("c.kind=%s")
        params.append(kind)

    if q:
        where.append("(LOWER(c.title) LIKE %s OR LOWER(c.summary) LIKE %s)")
        like = f"%{q}%"
        params.extend([like, like])

    sql = """
        SELECT
          c.id,
          c.kind,
          c.title,
          c.summary,
          c.image_path,
          c.doc_path,
          c.external_link,
          c.published_at,
          c.created_at,
          c.updated_at
        FROM law_content c
    """
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY COALESCE(c.published_at, c.created_at) DESC, c.id DESC"

    cur = mysql.connection.cursor()
    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    cur.close()

    items = []
    for r in rows:
        items.append({
            "id": r[0],
            "kind": r[1],
            "title": r[2],
            "summary": r[3],
            "image_path": r[4],
            "doc_path": r[5],
            "external_link": r[6],
            "published_at": r[7],
            "created_at": r[8],
            "updated_at": r[9],
        })

    return render_template("content_list.html", items=items, active_page="content_list", current_kind=kind, q=q)

# ------------- Full View -------------
@admin_bp.route("/content/<int:content_id>")
@login_required
def admin_content_view(content_id: int):
    _ensure_mysql()
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
          id, kind, title, summary, body, image_path, doc_path,
          external_link, author_admin_id, published_at, created_at, updated_at
        FROM law_content
        WHERE id=%s
        LIMIT 1
    """, (content_id,))
    r = cur.fetchone()
    cur.close()

    if not r:
        flash("Content not found.", "error")
        return redirect(url_for("admin.admin_content_list"))

    item = {
        "id": r[0], "kind": r[1], "title": r[2], "summary": r[3], "body": r[4],
        "image_path": r[5], "doc_path": r[6], "external_link": r[7],
        "author_admin_id": r[8], "published_at": r[9],
        "created_at": r[10], "updated_at": r[11],
    }
    return render_template("content_view.html", item=item, active_page="content_list")

# ------------- Edit / Update -------------
@admin_bp.route("/content/<int:content_id>/edit", methods=["GET", "POST"])
@login_required
def admin_content_edit(content_id: int):
    _ensure_mysql()

    # Load existing
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
          id, kind, title, summary, body, image_path, doc_path,
          external_link, published_at
        FROM law_content
        WHERE id=%s
        LIMIT 1
    """, (content_id,))
    row = cur.fetchone()
    cur.close()

    if not row:
        flash("Content not found.", "error")
        return redirect(url_for("admin.admin_content_list"))

    # Map tuple to dict
    current = {
        "id": row[0], "kind": row[1], "title": row[2], "summary": row[3],
        "body": row[4], "image_path": row[5], "doc_path": row[6],
        "external_link": row[7], "published_at": row[8],
    }

    if request.method == "GET":
        return render_template("content_edit.html", item=current, active_page="content_list")

    # POST: update
    kind = (request.form.get("kind") or "").strip().lower()
    title = (request.form.get("title") or "").strip()
    summary = (request.form.get("summary") or "").strip()
    body = (request.form.get("body") or "").strip()
    external_link = (request.form.get("external_link") or "").strip()
    published = (request.form.get("published") == "on")

    if kind not in ("update", "document", "news", "image"):
        flash("Please select a valid type.", "error")
        return redirect(request.referrer or url_for("admin.admin_content_list"))
    if not title:
        flash("Title is required.", "error")
        return redirect(request.referrer or url_for("admin.admin_content_list"))

    # File actions
    remove_image = request.form.get("remove_image") == "on"
    remove_doc = request.form.get("remove_doc") == "on"

    new_img_file = request.files.get("image_file")
    new_doc_file = request.files.get("doc_file")

    image_path = current["image_path"]
    doc_path = current["doc_path"]

    # Replace or remove image
    if new_img_file and new_img_file.filename:
        new_path, err = _save_upload(new_img_file, IMG_SUBDIR, ALLOWED_IMAGE_EXT)
        if err:
            flash(err, "error")
            return redirect(request.referrer or url_for("admin.admin_content_edit", content_id=content_id))
        # delete old
        _delete_file(image_path)
        image_path = new_path
    elif remove_image:
        _delete_file(image_path)
        image_path = None

    # Replace or remove document
    if new_doc_file and new_doc_file.filename:
        new_path, err = _save_upload(new_doc_file, DOC_SUBDIR, ALLOWED_DOC_EXT)
        if err:
            flash(err, "error")
            return redirect(request.referrer or url_for("admin.admin_content_edit", content_id=content_id))
        _delete_file(doc_path)
        doc_path = new_path
    elif remove_doc:
        _delete_file(doc_path)
        doc_path = None

    # Enforce type requirements after considering replacements/removals
    if kind == "image" and not image_path:
        flash("Image posts require an image.", "error")
        return redirect(request.referrer or url_for("admin.admin_content_edit", content_id=content_id))
    if kind == "document" and not doc_path:
        flash("Document posts require a document.", "error")
        return redirect(request.referrer or url_for("admin.admin_content_edit", content_id=content_id))

    published_at = datetime.now() if published else None

    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            UPDATE law_content
               SET kind=%s,
                   title=%s,
                   summary=%s,
                   body=%s,
                   image_path=%s,
                   doc_path=%s,
                   external_link=%s,
                   published_at=%s
             WHERE id=%s
        """, (kind, title, summary or None, body or None,
              image_path, doc_path, external_link or None,
              published_at, content_id))
        mysql.connection.commit()
        flash("Content updated.", "success")
    except Exception as exc:
        mysql.connection.rollback()
        current_app.logger.exception("admin_content_edit error: %s", exc)
        flash("DB error while updating content.", "error")
    finally:
        cur.close()

    return redirect(url_for("admin.admin_content_edit", content_id=content_id))

# ------------- Delete -------------
@admin_bp.route("/content/<int:content_id>/delete", methods=["POST"])
@login_required
def admin_content_delete(content_id: int):
    _ensure_mysql()

    # Get paths to delete files
    cur = mysql.connection.cursor()
    cur.execute("SELECT image_path, doc_path FROM law_content WHERE id=%s", (content_id,))
    r = cur.fetchone()
    if not r:
        cur.close()
        flash("Content not found.", "error")
        return redirect(url_for("admin.admin_content_list"))

    image_path, doc_path = r[0], r[1]

    try:
        cur.execute("DELETE FROM law_content WHERE id=%s", (content_id,))
        mysql.connection.commit()
        cur.close()
        # remove files after DB deletion
        _delete_file(image_path)
        _delete_file(doc_path)
        flash("Content deleted.", "success")
    except Exception as exc:
        mysql.connection.rollback()
        cur.close()
        current_app.logger.exception("admin_content_delete error: %s", exc)
        flash("DB error while deleting content.", "error")

    return redirect(url_for("admin.admin_content_list"))
