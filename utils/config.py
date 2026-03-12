"""Configuration for Odoo API"""
ODOO_URL = "http://103.82.38.96:8069//jsonrpc"
HEADERS = {"Content-Type": "application/json"}
DB = "odoo-crm-erp"
USERNAME = "odoo"
PASSWORD = "odoo"

# Cache để lưu thông tin quyền của user (có thể dùng Redis trong production)
user_permissions_cache = {}
