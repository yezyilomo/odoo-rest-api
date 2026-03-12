"""Employees CRUD routes"""
from flask import Blueprint, request, jsonify
from utils.odoo_helper import execute_odoo_kw, check_odoo_error
from utils.auth_helper import check_permission, token_required
from utils.config import PASSWORD

employees_bp = Blueprint('employees', __name__)


@employees_bp.route("/employees", methods=["GET"])
@check_permission('hr.employee', 'read', use_cache=False)
def get_employees(current_user):
    """Lấy danh sách employees - yêu cầu token và quyền read"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        
        # Lấy query parameters
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        fields = request.args.get('fields', 'id,name,work_email,work_phone,department_id,job_id,company_id')
        fields_list = [f.strip() for f in fields.split(',')]
        
        res = execute_odoo_kw(
            uid, user_password, "hr.employee", "search_read",
            [[]], {"fields": fields_list, "limit": limit, "offset": offset}
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


@employees_bp.route("/employees/<int:employee_id>", methods=["GET"])
@check_permission('hr.employee', 'read', use_cache=False)
def get_employee(current_user, employee_id):
    """Lấy thông tin 1 employee cụ thể"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        
        res = execute_odoo_kw(
            uid, user_password, "hr.employee", "read",
            [employee_id], {
                "fields": [
                    "id", "name", "work_email", "work_phone", 
                    "department_id", "job_id", "user_id", "company_id"
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
            return jsonify({'error': 'Employee không tồn tại'}), 404
        
        return jsonify({
            'data': result[0],
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@employees_bp.route("/employees", methods=["POST"])
@check_permission('hr.employee', 'create', use_cache=False)
def create_employee(current_user):
    """Tạo employee mới"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Vui lòng cung cấp dữ liệu employee'}), 400
        
        # Tạo employee
        res = execute_odoo_kw(
            uid, user_password, "hr.employee", "create",
            [data], {}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền tạo employee',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi tạo employee',
                'odoo_error': error_message
            }), status_code
        
        employee_id = res.get("result")
        return jsonify({
            'message': 'Tạo employee thành công',
            'id': employee_id,
            'user': current_user['username']
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@employees_bp.route("/employees/<int:employee_id>", methods=["PUT"])
@check_permission('hr.employee', 'write', use_cache=False)
def update_employee(current_user, employee_id):
    """Cập nhật employee"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Vui lòng cung cấp dữ liệu cập nhật'}), 400
        
        # Cập nhật employee
        res = execute_odoo_kw(
            uid, user_password, "hr.employee", "write",
            [[employee_id], data], {}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền cập nhật employee',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi cập nhật employee',
                'odoo_error': error_message
            }), status_code
        
        return jsonify({
            'message': 'Cập nhật employee thành công',
            'id': employee_id,
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@employees_bp.route("/employees/<int:employee_id>", methods=["DELETE"])
@check_permission('hr.employee', 'unlink', use_cache=False)
def delete_employee(current_user, employee_id):
    """Xóa employee"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        
        # Xóa employee
        res = execute_odoo_kw(
            uid, user_password, "hr.employee", "unlink",
            [[employee_id]], {}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền xóa employee',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi xóa employee',
                'odoo_error': error_message
            }), status_code
        
        return jsonify({
            'message': 'Xóa employee thành công',
            'id': employee_id,
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500
