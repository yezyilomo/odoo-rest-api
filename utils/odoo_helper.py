"""Helper functions for Odoo API calls"""
import json
import requests
from .config import ODOO_URL, HEADERS, DB, PASSWORD


def check_odoo_error(response):
    """
    Kiểm tra lỗi từ response của Odoo, đặc biệt là lỗi Access Denied
    Trả về (has_error, error_message, status_code)
    """
    if 'error' not in response:
        return False, None, None
    
    error_data = response.get('error', {})
    error_message = str(error_data.get('data', {}).get('message', ''))
    
    # Kiểm tra lỗi Access Denied
    if any(keyword in error_message for keyword in ['Access Denied', 'access denied', 'Access denied']):
        return True, error_message, 403
    
    # Các lỗi khác
    return True, error_message, 400


def odoo_login(username=None, password=None):
    """Login vào Odoo và trả về user ID"""
    from .config import USERNAME
    
    login_username = username or USERNAME
    login_password = password or PASSWORD
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "common",
            "method": "login",
            "args": [DB, login_username, login_password]
        },
        "id": 1,
    }
    res = requests.post(ODOO_URL, data=json.dumps(payload), headers=HEADERS).json()
    return res.get("result")


def get_user_info(uid, password):
    """Lấy thông tin user và groups từ Odoo"""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                DB,
                uid,
                password,
                "res.users",
                "read",
                [uid],
                {"fields": ["id", "name", "login", "groups_id", "is_superuser"]},
            ],
        },
        "id": 2,
    }
    res = requests.post(ODOO_URL, data=json.dumps(payload), headers=HEADERS).json()
    if 'error' in res:
        return None
    return res.get("result", [{}])[0] if res.get("result") else None


def get_user_groups(uid, password):
    """Lấy danh sách groups của user"""
    user_info = get_user_info(uid, password)
    if not user_info:
        return []
    
    group_ids = user_info.get('groups_id', [])
    if not group_ids:
        return []

    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                DB,
                uid,
                password,
                "res.groups",
                "read",
                group_ids,
                {"fields": ["id", "name", "full_name", "category_id"]},
            ],
        },
        "id": 3,
    }
    res = requests.post(ODOO_URL, data=json.dumps(payload), headers=HEADERS).json()
    if 'error' in res:
        return []
    return res.get("result", [])


def execute_odoo_kw(uid, password, model, method, args_list, kwargs_dict):
    """Thực hiện execute_kw trên Odoo"""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                DB,
                uid,
                password,
                model,
                method,
                args_list,
                kwargs_dict,
            ],
        },
        "id": 1,
    }
    res = requests.post(ODOO_URL, data=json.dumps(payload), headers=HEADERS).json()
    return res
