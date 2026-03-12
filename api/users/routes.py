"""Users CRUD routes - res.users model"""
from flask import Blueprint, request, jsonify
from utils.odoo_helper import execute_odoo_kw, check_odoo_error
from utils.auth_helper import check_permission, token_required
from utils.config import PASSWORD

users_bp = Blueprint('users', __name__)


@users_bp.route("/users", methods=["GET"])
@check_permission('res.users', 'read', use_cache=False)
def get_users(current_user):
    """Lấy danh sách users - yêu cầu token và quyền read"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        
        # Lấy query parameters
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        fields = request.args.get('fields', 'id,name,login,email,phone')
        fields_list = [f.strip() for f in fields.split(',')]
        
        # Lấy filter nếu có
        domain = []
        if request.args.get('active'):
            domain.append(['active', '=', request.args.get('active') == 'true'])
        if request.args.get('search'):
            search_term = request.args.get('search')
            # Search trên name và login
            search_domain = [
                '|',
                ['name', 'ilike', search_term],
                ['login', 'ilike', search_term]
            ]
            if domain:
                domain.append(search_domain)
            else:
                domain = search_domain
        
        # Nếu domain rỗng, dùng []
        if not domain:
            domain = []
        
        res = execute_odoo_kw(
            uid, user_password, "res.users", "search_read",
            [domain], {"fields": fields_list, "limit": limit, "offset": offset}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền truy cập dữ liệu này',
                    'message': 'Quyền đã bị khóa trên Odoo.',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi truy vấn dữ liệu từ Odoo',
                'odoo_error': error_message
            }), status_code
        
        result = res.get("result", [])
        
        # Kiểm tra kết quả: Nếu chỉ trả về 1 record (chính user đó), không có quyền đọc users khác
        if len(result) == 1 and result[0].get('id') == uid:
            return jsonify({
                'error': 'Bạn không có quyền xem danh sách users',
                'message': 'Bạn chỉ có quyền xem thông tin của chính mình. Quyền admin đã bị khóa trên Odoo.',
                'model': 'res.users',
                'operation': 'read'
            }), 403
        
        return jsonify({
            'data': result,
            'count': len(result),
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@users_bp.route("/users/<int:user_id>", methods=["GET"])
@check_permission('res.users', 'read', use_cache=False)
def get_user(current_user, user_id):
    """Lấy thông tin 1 user cụ thể"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        
        res = execute_odoo_kw(
            uid, user_password, "res.users", "read",
            [user_id], {
                "fields": [
                    "id", "name", "login", "email", "phone",
                    "active", "groups_id", "is_superuser", "partner_id"
                ]
            }
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền truy cập dữ liệu này',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi truy vấn dữ liệu từ Odoo',
                'odoo_error': error_message
            }), status_code
        
        result = res.get("result", [])
        if not result:
            return jsonify({'error': 'User không tồn tại'}), 404
        
        return jsonify({
            'data': result[0],
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@users_bp.route("/users", methods=["POST"])
@check_permission('res.users', 'create', use_cache=False)
def create_user(current_user):
    """Tạo user mới"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Vui lòng cung cấp dữ liệu user'}), 400
        
        if not data.get('name'):
            return jsonify({'error': 'Tên user là bắt buộc'}), 400
        
        if not data.get('login'):
            return jsonify({'error': 'Login (username/email) là bắt buộc'}), 400
        
        # Tạo user
        res = execute_odoo_kw(
            uid, user_password, "res.users", "create",
            [data], {}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền tạo user',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi tạo user',
                'odoo_error': error_message
            }), status_code
        
        user_id = res.get("result")
        return jsonify({
            'message': 'Tạo user thành công',
            'id': user_id,
            'user': current_user['username']
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
@check_permission('res.users', 'write', use_cache=False)
def update_user(current_user, user_id):
    """Cập nhật user"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Vui lòng cung cấp dữ liệu cập nhật'}), 400
        
        # Không cho phép cập nhật password qua endpoint này
        if 'password' in data:
            return jsonify({
                'error': 'Không thể cập nhật password qua endpoint này',
                'message': 'Vui lòng sử dụng endpoint /api/users/<id>/change-password để đổi password'
            }), 400
        
        # Cập nhật user
        res = execute_odoo_kw(
            uid, user_password, "res.users", "write",
            [[user_id], data], {}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền cập nhật user',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi cập nhật user',
                'odoo_error': error_message
            }), status_code
        
        return jsonify({
            'message': 'Cập nhật user thành công',
            'id': user_id,
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
@check_permission('res.users', 'unlink', use_cache=False)
def delete_user(current_user, user_id):
    """Xóa user (thực chất là deactivate)"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        
        # Trong Odoo, thường không xóa user mà chỉ deactivate
        # Nếu muốn xóa thật, dùng unlink
        # Ở đây ta sẽ deactivate user thay vì xóa
        res = execute_odoo_kw(
            uid, user_password, "res.users", "write",
            [[user_id], {'active': False}], {}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền xóa/deactivate user',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi xóa/deactivate user',
                'odoo_error': error_message
            }), status_code
        
        return jsonify({
            'message': 'Deactivate user thành công',
            'id': user_id,
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@users_bp.route("/users/<int:user_id>/change-password", methods=["POST"])
@check_permission('res.users', 'write', use_cache=False)
def change_password(current_user, user_id):
    """Đổi password cho user"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Vui lòng cung cấp password mới'}), 400
        
        new_password = data.get('new_password')
        if not new_password:
            return jsonify({'error': 'new_password là bắt buộc'}), 400
        
        # Kiểm tra xem user có quyền đổi password của user này không
        # User chỉ có thể đổi password của chính mình hoặc phải là admin
        if user_id != uid and not current_user.get('is_superuser', False):
            # Kiểm tra quyền write trên user này
            check_res = execute_odoo_kw(
                uid, user_password, "res.users", "read",
                [user_id], {"fields": ["id"]}
            )
            if 'error' in check_res:
                return jsonify({
                    'error': 'Bạn không có quyền đổi password cho user này'
                }), 403
        
        # Đổi password bằng cách update field password
        # Trong Odoo, password được hash tự động
        res = execute_odoo_kw(
            uid, user_password, "res.users", "write",
            [[user_id], {'password': new_password}], {}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền đổi password',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi đổi password',
                'odoo_error': error_message
            }), status_code
        
        return jsonify({
            'message': 'Đổi password thành công',
            'id': user_id,
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500
