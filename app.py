import os, sys
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
from flask import Flask
from flask_bcrypt import Bcrypt
from config.db_config import init_db


try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from modules.admin import routes as admin_routes
from modules.lawyer import routes as lawyer_routes
from modules.user import routes as user_routes
from modules.admin import lawyer_routes as lawyer_mgmt_routes
from modules.admin import user_routes as user_mgmt_routes
from modules.user import assistant_route as assistant_routes
from modules.user import lawyer_booking_route as lawyer_booking_routes
from modules.user import content_public_routes as user_content_routes
from modules.lawyer import appointment_manage_route as appt_routes
from modules.user import appointments_route as user_appt_routes

app = Flask(__name__)
app.secret_key = 'secret_key'


app.config.update(
    MAIL_HOST="smtp.gmail.com",
    MAIL_PORT=465,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.environ.get("SMTP_USER"),
    MAIL_PASSWORD=os.environ.get("SMTP_PASS"),
    MAIL_FROM=os.environ.get("MAIL_FROM"),
    MAIL_SENDER_NAME="Legal Care",
)

bcrypt = Bcrypt(app)
mysql = init_db(app)


admin_routes.bcrypt = bcrypt
admin_routes.mysql = mysql
lawyer_routes.bcrypt = bcrypt
lawyer_routes.mysql = mysql
user_routes.bcrypt = bcrypt
user_routes.mysql = mysql
lawyer_mgmt_routes.bcrypt = bcrypt
lawyer_mgmt_routes.mysql = mysql
user_mgmt_routes.bcrypt = bcrypt
user_mgmt_routes.mysql = mysql
lawyer_booking_routes.bcrypt = bcrypt
lawyer_booking_routes.mysql = mysql
user_content_routes.mysql = mysql
user_content_routes.bcrypt = bcrypt
appt_routes.mysql = mysql
appt_routes.bcrypt = bcrypt
user_appt_routes.mysql = mysql
user_appt_routes.bcrypt = bcrypt


app.register_blueprint(admin_routes.admin_bp, url_prefix='/admin')
app.register_blueprint(lawyer_routes.lawyer_bp, url_prefix='/lawyer')
app.register_blueprint(user_routes.user_bp, url_prefix='/user')
app.register_blueprint(lawyer_mgmt_routes.lawyer_mgmt_bp, url_prefix="/admin")
app.register_blueprint(user_mgmt_routes.user_mgmt_bp, url_prefix='/admin')
app.register_blueprint(assistant_routes.assistant_bp, url_prefix="/assistant")
app.register_blueprint(lawyer_booking_routes.user_lawyers_bp, url_prefix="/user")
app.register_blueprint(user_content_routes.user_content_bp, url_prefix="/user")
app.register_blueprint(appt_routes.lawyer_appt_bp, url_prefix="/lawyer")
app.register_blueprint(user_appt_routes.user_appt_bp, url_prefix="/user")

if __name__ == '__main__':
    app.run(debug=True)
