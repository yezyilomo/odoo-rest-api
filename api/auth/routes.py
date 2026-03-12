"""Authentication routes"""
from flask import Blueprint, request, jsonify, current_app
from utils.odoo_helper import odoo_login, get_user_info, get_user_groups
from utils.auth_helper import generate_token, token_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """API login để lấy token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Vui lòng cung cấp username và password'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username và password là bắt buộc'}), 400
        
        # Kiểm tra đăng nhập với Odoo
        uid = odoo_login(username, password)
        
        if not uid:
            return jsonify({'error': 'Đăng nhập thất bại. Kiểm tra lại username và password'}), 401
        
        # Lấy thông tin user và groups
        user_info = get_user_info(uid, password)
        groups = []
        is_superuser = False
        
        if user_info:
            # Trường is_superuser trong Odoo thường không được dùng, nên
            # ta bổ sung logic: nếu user thuộc nhóm Administration / Settings
            # thì coi như superuser trong hệ thống API này.
            is_superuser = user_info.get('is_superuser', False)
            groups_data = get_user_groups(uid, password)
            groups = [g.get('full_name', g.get('name', '')) for g in groups_data]
            
            if not is_superuser:
                admin_keywords = [
                    'Administration / Settings',
                    'Administration/Settings',
                    'Settings',
                ]
                lower_groups = [g.lower() for g in groups]
                if any(any(k.lower() in g for g in lower_groups) for k in admin_keywords):
                    is_superuser = True
        
        # Tạo token
        token = generate_token(username, uid, password, groups, is_superuser, current_app.config['SECRET_KEY'])
        
        return jsonify({
            'message': 'Đăng nhập thành công',
            'token': token,
            'user': {
                'username': username,
                'uid': uid,
                'groups': groups,
                'is_superuser': is_superuser
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user(current_user):
    """Lấy thông tin user hiện tại"""
    return jsonify({
        'username': current_user['username'],
        'uid': current_user['uid'],
        'groups': current_user.get('groups', []),
        'is_superuser': current_user.get('is_superuser', False)
    }), 200
