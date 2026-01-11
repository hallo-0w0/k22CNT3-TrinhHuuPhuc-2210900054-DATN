"""
Users Routes - CRUD
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.user import User
from models.role import Role
from models.member_level import MemberLevel
from utils.decorators import roles_required, admin_required
from utils.helpers import create_activity_log, paginate_query

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def get_users():
    """Lấy danh sách users (ADMIN only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role_filter = request.args.get('role')
        member_level_filter = request.args.get('member_level')
        search = request.args.get('search')
        
        query = User.query
        
        # Filter by role
        if role_filter:
            role = Role.query.filter_by(role_name=role_filter.upper()).first()
            if role:
                query = query.filter_by(role_id=role.role_id)
        
        # Filter by member level
        if member_level_filter:
            member_level = MemberLevel.query.filter_by(level_code=member_level_filter.upper()).first()
            if member_level:
                query = query.filter_by(member_level_id=member_level.member_level_id)
        
        # Search
        if search:
            query = query.filter(
                db.or_(
                    User.username.like(f'%{search}%'),
                    User.email.like(f'%{search}%'),
                    User.full_name.like(f'%{search}%')
                )
            )
        
        result = paginate_query(query.order_by(User.created_at.desc()), page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy danh sách users',
            'error': str(e)
        }), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Lấy thông tin chi tiết user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        user = User.query.get_or_404(user_id)
        
        # Kiểm tra quyền: chỉ được xem chính mình hoặc ADMIN
        if current_user.user_id != user_id and not current_user.is_admin():
            return jsonify({
                'message': 'Không có quyền xem thông tin user này',
                'error': 'insufficient_permissions'
            }), 403
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy thông tin user',
            'error': str(e)
        }), 500

@users_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_user():
    """Tạo user mới (ADMIN only)"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['username', 'email', 'password', 'full_name', 'role_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'message': f'Thiếu trường {field}',
                    'error': 'missing_field'
                }), 400
        
        # Check username exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'message': 'Tên đăng nhập đã tồn tại',
                'error': 'username_exists'
            }), 400
        
        # Check email exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'message': 'Email đã tồn tại',
                'error': 'email_exists'
            }), 400
        
        # Check role exists
        role = Role.query.get(data['role_id'])
        if not role:
            return jsonify({
                'message': 'Role không tồn tại',
                'error': 'role_not_found'
            }), 404
        
        # Check member_level_id nếu có
        member_level_id = data.get('member_level_id')
        if member_level_id:
            member_level = MemberLevel.query.get(member_level_id)
            if not member_level:
                return jsonify({
                    'message': 'Member level không tồn tại',
                    'error': 'member_level_not_found'
                }), 404
            
            # Chỉ CUSTOMER mới có member level
            if role.role_name != 'CUSTOMER':
                return jsonify({
                    'message': 'Chỉ CUSTOMER mới có thể có member level',
                    'error': 'invalid_member_level'
                }), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            phone_number=data.get('phone_number'),
            address=data.get('address'),
            role_id=data['role_id'],
            member_level_id=member_level_id
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Activity log
        current_user_id = get_jwt_identity()
        create_activity_log(current_user_id, 'CREATE', 'User', user.user_id, f'Tạo user: {user.username}')
        
        return jsonify({
            'message': 'Tạo user thành công',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi tạo user',
            'error': str(e)
        }), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Cập nhật user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        user = User.query.get_or_404(user_id)
        
        # Kiểm tra quyền: chỉ được sửa chính mình hoặc ADMIN
        if current_user.user_id != user_id and not current_user.is_admin():
            return jsonify({
                'message': 'Không có quyền sửa user này',
                'error': 'insufficient_permissions'
            }), 403
        
        data = request.get_json()
        
        # Update fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'phone_number' in data:
            user.phone_number = data.get('phone_number')
        if 'address' in data:
            user.address = data.get('address')
        if 'email' in data:
            # Check email unique
            if User.query.filter(User.email == data['email'], User.user_id != user_id).first():
                return jsonify({
                    'message': 'Email đã tồn tại',
                    'error': 'email_exists'
                }), 400
            user.email = data['email']
        
        # Chỉ ADMIN mới được sửa các trường này
        if current_user.is_admin():
            if 'role_id' in data:
                role = Role.query.get(data['role_id'])
                if not role:
                    return jsonify({
                        'message': 'Role không tồn tại',
                        'error': 'role_not_found'
                    }), 404
                user.role_id = data['role_id']
            
            if 'member_level_id' in data:
                member_level_id = data.get('member_level_id')
                if member_level_id:
                    member_level = MemberLevel.query.get(member_level_id)
                    if not member_level:
                        return jsonify({
                            'message': 'Member level không tồn tại',
                            'error': 'member_level_not_found'
                        }), 404
                    # Chỉ CUSTOMER mới có member level
                    if user.role.role_name != 'CUSTOMER':
                        return jsonify({
                            'message': 'Chỉ CUSTOMER mới có thể có member level',
                            'error': 'invalid_member_level'
                        }), 400
                user.member_level_id = member_level_id
            
            if 'is_active' in data:
                user.is_active = data['is_active']
            if 'is_locked' in data:
                user.is_locked = data['is_locked']
        
        # Update password nếu có
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.commit()
        
        # Activity log
        create_activity_log(current_user_id, 'UPDATE', 'User', user.user_id, f'Cập nhật user: {user.username}')
        
        return jsonify({
            'message': 'Cập nhật user thành công',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi cập nhật user',
            'error': str(e)
        }), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Xóa user (ADMIN only)"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Không cho xóa chính mình
        current_user_id = get_jwt_identity()
        if user.user_id == current_user_id:
            return jsonify({
                'message': 'Không thể xóa chính mình',
                'error': 'cannot_delete_self'
            }), 400
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        # Activity log
        create_activity_log(current_user_id, 'DELETE', 'User', user_id, f'Xóa user: {username}')
        
        return jsonify({
            'message': 'Xóa user thành công'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi xóa user',
            'error': str(e)
        }), 500
