"""Departments CRUD routes - hr.department model"""
from flask import Blueprint, request, jsonify
from utils.odoo_helper import execute_odoo_kw, check_odoo_error
from utils.auth_helper import check_permission, token_required
from utils.config import PASSWORD

departments_bp = Blueprint('departments', __name__)


@departments_bp.route("/departments", methods=["GET"])
@check_permission('hr.department', 'read', use_cache=False)
def get_departments(current_user):
    """Lấy danh sách departments - yêu cầu token và quyền read"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        
        # Lấy query parameters
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        fields = request.args.get('fields', 'id,name,manager_id,member_ids')
        fields_list = [f.strip() for f in fields.split(',')]
        
        # Lấy filter nếu có
        domain = []
        if request.args.get('search'):
            search_term = request.args.get('search')
            search_domain = [
                ['name', 'ilike', search_term]
            ]
            if domain:
                domain.append(search_domain)
            else:
                domain = search_domain
        
        # Nếu domain rỗng, dùng []
        if not domain:
            domain = []
        
        res = execute_odoo_kw(
            uid, user_password, "hr.department", "search_read",
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
        return jsonify({
            'data': result,
            'count': len(result),
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@departments_bp.route("/departments/<int:department_id>", methods=["GET"])
@check_permission('hr.department', 'read', use_cache=False)
def get_department(current_user, department_id):
    """Lấy thông tin 1 department cụ thể"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        
        res = execute_odoo_kw(
            uid, user_password, "hr.department", "read",
            [department_id], {
                "fields": [
                    "id", "name", "manager_id", "member_ids",
                    "company_id", "parent_id", "note"
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
            return jsonify({'error': 'Department không tồn tại'}), 404
        
        return jsonify({
            'data': result[0],
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@departments_bp.route("/departments", methods=["POST"])
@check_permission('hr.department', 'create', use_cache=False)
def create_department(current_user):
    """Tạo department mới"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Vui lòng cung cấp dữ liệu department'}), 400
        
        if not data.get('name'):
            return jsonify({'error': 'Tên department là bắt buộc'}), 400
        
        # Tạo department
        res = execute_odoo_kw(
            uid, user_password, "hr.department", "create",
            [data], {}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền tạo department',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi tạo department',
                'odoo_error': error_message
            }), status_code
        
        department_id = res.get("result")
        return jsonify({
            'message': 'Tạo department thành công',
            'id': department_id,
            'user': current_user['username']
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@departments_bp.route("/departments/<int:department_id>", methods=["PUT"])
@check_permission('hr.department', 'write', use_cache=False)
def update_department(current_user, department_id):
    """Cập nhật department"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Vui lòng cung cấp dữ liệu cập nhật'}), 400
        
        # Cập nhật department
        res = execute_odoo_kw(
            uid, user_password, "hr.department", "write",
            [[department_id], data], {}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền cập nhật department',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi cập nhật department',
                'odoo_error': error_message
            }), status_code
        
        return jsonify({
            'message': 'Cập nhật department thành công',
            'id': department_id,
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@departments_bp.route("/departments/<int:department_id>", methods=["DELETE"])
@check_permission('hr.department', 'unlink', use_cache=False)
def delete_department(current_user, department_id):
    """Xóa department"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        
        # Xóa department
        res = execute_odoo_kw(
            uid, user_password, "hr.department", "unlink",
            [[department_id]], {}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền xóa department',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi xóa department',
                'odoo_error': error_message
            }), status_code
        
        return jsonify({
            'message': 'Xóa department thành công',
            'id': department_id,
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500
