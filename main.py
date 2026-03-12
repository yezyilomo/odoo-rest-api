"""Main Flask application"""
from flask import Flask, jsonify
from api.auth.routes import auth_bp
from api.employees.routes import employees_bp
from api.contacts.routes import contacts_bp
from api.users.routes import users_bp
from api.departments.routes import departments_bp
from api.approvals.routes import approvals_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-change-this-in-production"  # Thay đổi key này trong production

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(employees_bp, url_prefix="/api")
app.register_blueprint(contacts_bp, url_prefix="/api")
app.register_blueprint(users_bp, url_prefix="/api")
app.register_blueprint(departments_bp, url_prefix="/api")
app.register_blueprint(approvals_bp, url_prefix="/api")


@app.route("/health", methods=["GET"])
def health():
    """Endpoint kiểm tra server có hoạt động không"""
    return jsonify({"status": "ok", "message": "Server đang chạy"}), 200


if __name__ == "__main__":
    app.run(port=5001, debug=True)
