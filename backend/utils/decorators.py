"""
Decorators cho phân quyền và xác thực
"""
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User
from models.role import Role

def roles_required(*roles):
    """
    Decorator để kiểm tra role của user
    
    Usage:
        @roles_required('ADMIN', 'STAFF')
        def my_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verify JWT token
            verify_jwt_in_request()
            
            # Get current user
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({
                    'message': 'Người dùng không tồn tại',
                    'error': 'user_not_found'
                }), 404
            
            if not user.is_active:
                return jsonify({
                    'message': 'Tài khoản đã bị khóa',
                    'error': 'account_locked'
                }), 403
            
            # Check role
            if not user.role or user.role.role_name not in roles:
                return jsonify({
                    'message': 'Không có quyền truy cập',
                    'error': 'insufficient_permissions'
                }), 403
            
            # Add user to kwargs
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def member_level_required(*member_levels):
    """
    Decorator để kiểm tra member level (chỉ cho CUSTOMER)
    Lưu ý: Decorator này KHÔNG dùng để phân quyền API, chỉ dùng cho business logic
    
    Usage:
        @member_level_required('GOLD', 'DIAMOND')
        def my_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verify JWT token
            verify_jwt_in_request()
            
            # Get current user
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({
                    'message': 'Người dùng không tồn tại',
                    'error': 'user_not_found'
                }), 404
            
            # Check if user is CUSTOMER
            if not user.is_customer():
                return jsonify({
                    'message': 'Chỉ khách hàng mới có member level',
                    'error': 'not_customer'
                }), 403
            
            # Check member level
            if not user.member_level or user.member_level.level_code not in member_levels:
                return jsonify({
                    'message': 'Cấp độ thành viên không đủ',
                    'error': 'insufficient_member_level'
                }), 403
            
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator shortcut cho ADMIN only"""
    return roles_required('ADMIN')(f)

def staff_or_admin_required(f):
    """Decorator shortcut cho STAFF hoặc ADMIN"""
    return roles_required('STAFF', 'ADMIN')(f)

def customer_or_staff_or_admin_required(f):
    """Decorator shortcut cho CUSTOMER, STAFF hoặc ADMIN"""
    return roles_required('CUSTOMER', 'STAFF', 'ADMIN')(f)
