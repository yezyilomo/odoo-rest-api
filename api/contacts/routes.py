"""Contacts CRUD routes - res.partner model"""
from flask import Blueprint, request, jsonify
from utils.odoo_helper import execute_odoo_kw, check_odoo_error
from utils.auth_helper import check_permission, token_required
from utils.config import PASSWORD

contacts_bp = Blueprint('contacts', __name__)


@contacts_bp.route("/contacts", methods=["GET"])
@check_permission('res.partner', 'read', use_cache=False)
def get_contacts(current_user):
    """Lấy danh sách contacts - yêu cầu token và quyền read"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        
        # Lấy query parameters
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        fields = request.args.get('fields', 'id,name,email,phone,street,city,country_id')
        fields_list = [f.strip() for f in fields.split(',')]
        
        # Lấy filter nếu có
        domain = []
        
        # Thêm các filter AND
        if request.args.get('is_company'):
            domain.append(['is_company', '=', request.args.get('is_company') == 'true'])
        # Note: customer_rank và supplier_rank không có trong một số version Odoo
        # Có thể dùng filter khác nếu cần
        # if request.args.get('customer'):
        #     domain.append(['customer_rank', '>', 0])
        # if request.args.get('supplier'):
        #     domain.append(['supplier_rank', '>', 0])
        
        # Thêm search với OR conditions
        if request.args.get('search'):
            search_term = request.args.get('search')
            # Xây dựng domain OR đúng cách cho Odoo
            # Chỉ dùng các field phổ biến và chắc chắn có trong res.partner
            # Format cho 3 điều kiện OR: ['|', '|', c1, c2, c3]
            search_domain = [
                '|', '|',
                ['name', 'ilike', search_term],
                ['email', 'ilike', search_term],
                ['phone', 'ilike', search_term]
            ]
            
            # Kết hợp với domain hiện tại (AND logic)
            if domain:
                # Khi có cả filter và search, cần kết hợp với AND
                # Format: [filter1, filter2, ['|', '|', ...]]
                domain.append(search_domain)
            else:
                # Chỉ có search, dùng trực tiếp
                domain = search_domain
        
        res = execute_odoo_kw(
            uid, user_password, "res.partner", "search_read",
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


@contacts_bp.route("/contacts/<int:contact_id>", methods=["GET"])
@check_permission('res.partner', 'read', use_cache=False)
def get_contact(current_user, contact_id):
    """Lấy thông tin 1 contact cụ thể"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        
        res = execute_odoo_kw(
            uid, user_password, "res.partner", "read",
            [contact_id], {
                "fields": [
                    "id", "name", "email", "phone", 
                    "street", "street2", "city", "state_id", "country_id",
                    "zip", "is_company", "category_id", "comment"
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
            return jsonify({'error': 'Contact không tồn tại'}), 404
        
        return jsonify({
            'data': result[0],
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@contacts_bp.route("/contacts", methods=["POST"])
@check_permission('res.partner', 'create', use_cache=False)
def create_contact(current_user):
    """Tạo contact mới"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Vui lòng cung cấp dữ liệu contact'}), 400
        
        if not data.get('name'):
            return jsonify({'error': 'Tên contact là bắt buộc'}), 400
        
        # Tạo contact
        res = execute_odoo_kw(
            uid, user_password, "res.partner", "create",
            [data], {}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền tạo contact',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi tạo contact',
                'odoo_error': error_message
            }), status_code
        
        contact_id = res.get("result")
        return jsonify({
            'message': 'Tạo contact thành công',
            'id': contact_id,
            'user': current_user['username']
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@contacts_bp.route("/contacts/<int:contact_id>", methods=["PUT"])
@check_permission('res.partner', 'write', use_cache=False)
def update_contact(current_user, contact_id):
    """Cập nhật contact"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Vui lòng cung cấp dữ liệu cập nhật'}), 400
        
        # Cập nhật contact
        res = execute_odoo_kw(
            uid, user_password, "res.partner", "write",
            [[contact_id], data], {}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền cập nhật contact',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi cập nhật contact',
                'odoo_error': error_message
            }), status_code
        
        return jsonify({
            'message': 'Cập nhật contact thành công',
            'id': contact_id,
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500


@contacts_bp.route("/contacts/<int:contact_id>", methods=["DELETE"])
@check_permission('res.partner', 'unlink', use_cache=False)
def delete_contact(current_user, contact_id):
    """Xóa contact"""
    try:
        uid = current_user['uid']
        user_password = current_user.get('password', PASSWORD)
        
        # Xóa contact
        res = execute_odoo_kw(
            uid, user_password, "res.partner", "unlink",
            [[contact_id]], {}
        )
        
        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return jsonify({
                    'error': 'Bạn không có quyền xóa contact',
                    'odoo_error': error_message
                }), 403
            return jsonify({
                'error': 'Lỗi khi xóa contact',
                'odoo_error': error_message
            }), status_code
        
        return jsonify({
            'message': 'Xóa contact thành công',
            'id': contact_id,
            'user': current_user['username']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500
