"""Authentication and authorization helpers"""
import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from .config import PASSWORD, user_permissions_cache
from .odoo_helper import check_odoo_error, execute_odoo_kw


def generate_token(username, uid, password, groups=None, is_superuser=False, secret_key=None):
    """Tạo JWT token cho user"""
    payload = {
        'username': username,
        'uid': uid,
        'password': password,
        'groups': groups or [],
        'is_superuser': is_superuser,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def token_required(f):
    """Decorator để yêu cầu token cho các endpoint"""
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import current_app
        
        token = None
        
        # Lấy token từ header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Token không hợp lệ'}), 401
        
        if not token:
            return jsonify({'error': 'Token bị thiếu. Vui lòng đăng nhập'}), 401
        
        try:
            # Verify token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = {
                'username': data['username'],
                'uid': data['uid'],
                'password': data.get('password', PASSWORD),
                'groups': data.get('groups', []),
                'is_superuser': data.get('is_superuser', False)
            }
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token đã hết hạn. Vui lòng đăng nhập lại'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token không hợp lệ'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def check_access_rights(uid, password, model, operation='read'):
    """Kiểm tra quyền truy cập của user trên model"""
    try:
        res = execute_odoo_kw(
            uid, password, model, "check_access_rights",
            [operation], {"raise_exception": False}
        )
        
        if 'error' in res:
            error_data = res.get('error', {}).get('data', {})
            error_message = str(error_data.get('message', ''))
            
            if any(keyword in error_message for keyword in ['Access Denied', 'access denied']):
                return False
            
            if 'AttributeError' in error_message or 'method' in error_message.lower():
                return check_access_rights_fallback(uid, password, model, operation)
            
            return False
        
        result = res.get("result", False)
        has_access = bool(result)
        
        if has_access and model == 'res.users' and operation == 'read':
            return check_access_rights_fallback(uid, password, model, operation)
        
        return has_access
    except Exception as e:
        print(f"Error checking access rights: {e}")
        return check_access_rights_fallback(uid, password, model, operation)


def check_access_rights_fallback(uid, password, model, operation='read'):
    """Fallback: Kiểm tra quyền bằng cách thử thực hiện operation thực tế"""
    try:
        if operation == 'read':
            if model == 'res.users':
                res = execute_odoo_kw(
                    uid, password, model, "search_read",
                    [[]], {"fields": ["id"], "limit": 10}
                )
            else:
                res = execute_odoo_kw(
                    uid, password, model, "search",
                    [[]], {"limit": 0}
                )
        else:
            res = execute_odoo_kw(
                uid, password, model, "search",
                [[]], {"limit": 1}
            )
        
        has_error, error_message, _ = check_odoo_error(res)
        if has_error:
            return False
        
        if model == 'res.users' and operation == 'read':
            result = res.get("result", [])
            if len(result) == 1 and result[0].get('id') == uid:
                return False
            return len(result) > 1
        
        return True
    except Exception as e:
        print(f"Error in fallback check: {e}")
        return False


def check_permission(model, operation='read', use_cache=False):
    """Decorator để kiểm tra quyền truy cập model"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(current_user, *args, **kwargs):
            if current_user.get('is_superuser', False):
                return f(current_user, *args, **kwargs)
            
            uid = current_user['uid']
            password = current_user.get('password', PASSWORD)
            
            cache_key = f"{uid}_{model}_{operation}"
            if use_cache and cache_key in user_permissions_cache:
                has_access = user_permissions_cache[cache_key]
            else:
                has_access = check_access_rights(uid, password, model, operation)
                if use_cache:
                    user_permissions_cache[cache_key] = has_access
            
            if not has_access:
                return jsonify({
                    'error': f'Bạn không có quyền {operation} trên model {model}',
                    'model': model,
                    'operation': operation,
                    'message': 'Quyền đã bị khóa trên Odoo. Vui lòng liên hệ admin để được cấp quyền.'
                }), 403
            
            return f(current_user, *args, **kwargs)
        
        return decorated
    return decorator
