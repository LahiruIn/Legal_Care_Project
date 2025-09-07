from flask import Blueprint, render_template, request, url_for, redirect, flash
from math import ceil

mysql = None

user_content_bp = Blueprint(
    "user_content_bp",
    __name__,
    template_folder="templates",   
    static_url_path="/user_static",
)

def _need_mysql():
    if mysql is None:
        raise RuntimeError("mysql not set. In app.py: user_content_routes.mysql = mysql")

@user_content_bp.route("/content")
def content_list():
    """
    Public list of published content.
    Filters: ?kind=update|document|news|image, ?q=search
    Pagination: ?page=1 (page size 9)
    """
    _need_mysql()

    kind = (request.args.get("kind") or "").strip().lower()
    q = (request.args.get("q") or "").strip().lower()
    page = max(int(request.args.get("page", 1) or 1), 1)
    page_size = 9
    offset = (page - 1) * page_size

    where = ["c.published_at IS NOT NULL"]
    params = []

    if kind in ("update", "document", "news", "image"):
        where.append("c.kind=%s")
        params.append(kind)

    if q:
        where.append("(LOWER(c.title) LIKE %s OR LOWER(c.summary) LIKE %s)")
        like = f"%{q}%"
        params.extend([like, like])

    base_sql = """
        FROM law_content c
        WHERE {where}
    """.format(where=" AND ".join(where))

    # total count
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT COUNT(*) {base_sql}", tuple(params))
    total = cur.fetchone()[0]

    # page rows
    cur.execute(f"""
        SELECT
          c.id, c.kind, c.title, c.summary,
          c.image_path, c.doc_path, c.external_link,
          c.published_at, c.created_at
        {base_sql}
        ORDER BY COALESCE(c.published_at, c.created_at) DESC, c.id DESC
        LIMIT %s OFFSET %s
    """, tuple(params + [page_size, offset]))
    rows = cur.fetchall()
    cur.close()

    items = []
    for r in rows:
        items.append({
            "id": r[0], "kind": r[1], "title": r[2], "summary": r[3],
            "image_path": r[4], "doc_path": r[5], "external_link": r[6],
            "published_at": r[7], "created_at": r[8],
        })

    pages = max(1, ceil(total / page_size))

    return render_template(
        "content_list_public.html",
        items=items,
        total=total,
        page=page,
        pages=pages,
        current_kind=kind,
        q=q
    )


@user_content_bp.route("/content/<int:content_id>")
def content_view(content_id: int):
    """Public full view. Only for published items."""
    _need_mysql()
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
          id, kind, title, summary, body,
          image_path, doc_path, external_link,
          published_at, created_at, updated_at
        FROM law_content
        WHERE id=%s AND published_at IS NOT NULL
        LIMIT 1
    """, (content_id,))
    r = cur.fetchone()
    cur.close()

    if not r:
        flash("Content not found.", "error")
        return redirect(url_for("user_content_bp.content_list"))

    item = {
        "id": r[0], "kind": r[1], "title": r[2], "summary": r[3], "body": r[4],
        "image_path": r[5], "doc_path": r[6], "external_link": r[7],
        "published_at": r[8], "created_at": r[9], "updated_at": r[10]
    }
    return render_template("content_view_public.html", item=item)
