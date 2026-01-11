"""
Authentication Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from models.user import User
from models.role import Role
from utils.helpers import create_activity_log
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Đăng ký tài khoản khách hàng"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['username', 'email', 'password', 'full_name']
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
        
        # Get CUSTOMER role
        customer_role = Role.query.filter_by(role_name='CUSTOMER').first()
        if not customer_role:
            return jsonify({
                'message': 'Role CUSTOMER không tồn tại',
                'error': 'role_not_found'
            }), 500
        
        # Get SILVER member level (default)
        from models.member_level import MemberLevel
        silver_level = MemberLevel.query.filter_by(level_code='SILVER').first()
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            phone_number=data.get('phone_number'),
            address=data.get('address'),
            role_id=customer_role.role_id,
            member_level_id=silver_level.member_level_id if silver_level else None
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create activity log
        create_activity_log(user.user_id, 'CREATE', 'User', user.user_id, f'Đăng ký tài khoản: {user.username}')
        
        return jsonify({
            'message': 'Đăng ký thành công',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi đăng ký',
            'error': str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Đăng nhập"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({
                'message': 'Thiếu tên đăng nhập hoặc mật khẩu',
                'error': 'missing_credentials'
            }), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == data['username']) | (User.email == data['username'])
        ).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({
                'message': 'Tên đăng nhập hoặc mật khẩu không đúng',
                'error': 'invalid_credentials'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'message': 'Tài khoản đã bị khóa',
                'error': 'account_locked'
            }), 403
        
        if user.is_locked:
            return jsonify({
                'message': 'Tài khoản đã bị khóa',
                'error': 'account_locked'
            }), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.user_id)
        refresh_token = create_refresh_token(identity=user.user_id)
        
        # Create activity log
        create_activity_log(user.user_id, 'LOGIN', 'User', user.user_id, f'Đăng nhập: {user.username}')
        
        return jsonify({
            'message': 'Đăng nhập thành công',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi đăng nhập',
            'error': str(e)
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'message': 'Người dùng không tồn tại hoặc đã bị khóa',
                'error': 'user_not_found'
            }), 404
        
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Lỗi refresh token',
            'error': str(e)
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Lấy thông tin user hiện tại"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'message': 'Người dùng không tồn tại',
                'error': 'user_not_found'
            }), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy thông tin user',
            'error': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Đăng xuất (client sẽ xóa token)"""
    try:
        user_id = get_jwt_identity()
        
        # Create activity log
        create_activity_log(user_id, 'LOGOUT', 'User', user_id, 'Đăng xuất')
        
        return jsonify({
            'message': 'Đăng xuất thành công'
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Lỗi đăng xuất',
            'error': str(e)
        }), 500
