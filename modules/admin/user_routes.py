from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from markupsafe import Markup
from functools import wraps
from MySQLdb.cursors import DictCursor
from contextlib import closing
import base64

user_mgmt_bp = Blueprint(
    "user_mgmt",
    __name__,
    template_folder="admin/templates",  # Adjust path if needed
    static_folder="static",
    static_url_path="/admin_static"
)



# Initialize extensions (will be set by main app)
bcrypt = None
mysql = None

# ──────── Template Filters ────────
@user_mgmt_bp.app_template_filter("b64encode")
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
def render_user_template(template, **kwargs):
    kwargs.update({
        'username': session.get('username', 'Admin'),
        'active_page': 'users'
    })
    return render_template(template, **kwargs)

def get_db_connection():
    if not mysql or not hasattr(mysql, 'connection'):
        raise RuntimeError("Database connection not initialized")
    return mysql.connection

# ──────── Routes ────────

@user_mgmt_bp.route("/dashboard/users")
@login_required
def manage_users():
    try:
        # Query to select only the necessary columns: id, full_name, email, nic, and city
        with closing(get_db_connection().cursor(DictCursor)) as cur:
            cur.execute("""
                SELECT id, full_name, email, nic, city
                FROM users
                ORDER BY full_name
            """)
            users = cur.fetchall()

        # Log the users fetched from the database
        print(f"Fetched Users: {users}")  # This will print to your console/logs for debugging

        # If users are fetched, pass them to the template
        if users:
            print(f"Users found: {users}")  # Debugging line to check the user data
        else:
            print("No users found.")  # Debugging line to check if no users are fetched

        # Render the template with the fetched user data
        return render_user_template("dashboard_user.html", users=users)

    except Exception as e:
        # Log the error and display a flash message
        current_app.logger.error(f"Error loading users: {str(e)}", exc_info=True)
        flash("Error loading users. Showing empty list.", "error")
        return render_user_template("dashboard_user.html", users=[])


@user_mgmt_bp.route("/dashboard/users/view/<int:id>")
@login_required
def view_user(id):
    try:
        with closing(get_db_connection().cursor(DictCursor)) as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (id,))
            user = cur.fetchone()

        if not user:
            flash("User not found.", "error")
            return redirect(url_for('user_mgmt.manage_users'))

        return render_template(
            "view_user.html",
            user=user,
            username=session.get('username', 'Admin'),
            active_page='users'
        )

    except Exception as e:
        current_app.logger.error(f"Error retrieving user: {str(e)}", exc_info=True)
        flash("Error fetching user details.", "error")
        return redirect(url_for('user_mgmt.manage_users'))


@user_mgmt_bp.route("/dashboard/users/add", methods=["GET", "POST"])
@login_required
def add_user():
    if request.method == "POST":
        try:
            # Process form data
            data = {
                "full_name": request.form.get("full_name"),
                "email": request.form.get("email"),
                "phone": request.form.get("phone"),
                "address": request.form.get("address"),
                "username": request.form.get("username"),
                "password": bcrypt.generate_password_hash(request.form.get("password")).decode("utf-8"),
                "role": request.form.get("role"),
                "status": 1 if request.form.get("status") == "on" else 0
            }

            with closing(get_db_connection().cursor()) as cur:
                cur.execute("""
                    INSERT INTO user (full_name, email, phone, address, username, password, role, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, tuple(data.values()))
                get_db_connection().commit()

            flash("User added successfully.", "success")
            return redirect(url_for("user_mgmt.manage_users"))

        except Exception as e:
            get_db_connection().rollback()
            current_app.logger.error(f"Error adding user: {str(e)}", exc_info=True)
            flash(f"Error adding user: {str(e)}", "error")
            return redirect(url_for("user_mgmt.add_user"))

    return render_user_template("add_user.html")


@user_mgmt_bp.route("/dashboard/users/update/<int:id>", methods=["GET", "POST"])
@login_required
def update_user(id):
    # POST ➜ update the record
    if request.method == "POST":
        try:
            data = {
                "full_name": request.form.get("full_name"),
                "email": request.form.get("email"),
                "phone": request.form.get("phone"),
                "address": request.form.get("address"),
                "username": request.form.get("username"),
                "role": request.form.get("role"),
                "status": 1 if request.form.get("status") == "on" else 0
            }

            with closing(get_db_connection().cursor()) as cur:
                cur.execute("""
                    UPDATE user SET
                        full_name = %s,
                        email = %s,
                        phone = %s,
                        address = %s,
                        username = %s,
                        role = %s,
                        status = %s
                    WHERE id = %s
                """, (*data.values(), id))
                get_db_connection().commit()

            flash("User updated successfully.", "success")
            return redirect(url_for("user_mgmt.manage_users"))

        except Exception as e:
            get_db_connection().rollback()
            current_app.logger.error(f"Error updating user: {str(e)}", exc_info=True)
            flash(f"Error updating user: {str(e)}", "error")
            return redirect(url_for("user_mgmt.update_user", id=id))

    # GET ➜ load form with existing data
    try:
        with closing(get_db_connection().cursor(DictCursor)) as cur:
            cur.execute("SELECT * FROM user WHERE id = %s", (id,))
            user = cur.fetchone()

            if not user:
                flash("User not found.", "error")
                return redirect(url_for("user_mgmt.manage_users"))

            return render_user_template("update_user.html", user=user)

    except Exception as e:
        current_app.logger.error(f"Error retrieving user: {str(e)}", exc_info=True)
        flash(f"Error retrieving user: {str(e)}", "error")
        return redirect(url_for("user_mgmt.manage_users"))


@user_mgmt_bp.route("/dashboard/users/delete/<int:id>", methods=["POST"])
@login_required
def delete_user(id):
    try:
        # Deleting the user by ID
        with closing(get_db_connection().cursor()) as cur:
            cur.execute("DELETE FROM users WHERE id = %s", (id,))
            get_db_connection().commit()  # Commit the transaction

        flash("User deleted successfully.", "success")
    except Exception as e:
        # If there's an error, roll back the transaction and log the error
        get_db_connection().rollback()
        current_app.logger.error(f"Error deleting user: {str(e)}", exc_info=True)
        flash(f"Error deleting user: {str(e)}", "error")

    # Redirect to the manage users page after deletion
    return redirect(url_for("user_mgmt.manage_users"))

