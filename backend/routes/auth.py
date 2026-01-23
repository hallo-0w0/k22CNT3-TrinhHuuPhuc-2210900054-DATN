from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from backend import db
from backend.models.user import User, Role, MemberLevel
from werkzeug.security import generate_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Đăng ký tài khoản:
    - CUSTOMER: mặc định gán MemberLevel = SILVER
    - STAFF: member_level_id phải NULL (do trigger chỉ cho CUSTOMER)
    Body: { username, email, password, full_name, phone_number?, address?, register_type: 'CUSTOMER'|'STAFF' }
    """
    try:
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        full_name = (data.get('full_name') or '').strip()
        phone_number = (data.get('phone_number') or '').strip() or None
        address = (data.get('address') or '').strip() or None
        register_type = (data.get('register_type') or 'CUSTOMER').strip().upper()

        if register_type not in ['CUSTOMER', 'STAFF']:
            return jsonify({'error': 'register_type không hợp lệ (CUSTOMER hoặc STAFF)'}), 400

        if not username or not email or not password or not full_name:
            return jsonify({'error': 'username, email, password, full_name là bắt buộc'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Mật khẩu tối thiểu 6 ký tự'}), 400

        # Check unique
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username đã tồn tại'}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email đã tồn tại'}), 409

        role = Role.query.filter_by(role_name=register_type).first()
        if not role:
            return jsonify({'error': f'Role {register_type} chưa được seed trong DB'}), 500

        member_level_id = None
        if register_type == 'CUSTOMER':
            silver = MemberLevel.query.filter_by(level_code='SILVER').first()
            if not silver:
                return jsonify({'error': 'MemberLevel SILVER chưa được seed trong DB'}), 500
            member_level_id = silver.member_level_id

        # Hash password
        password_hash = generate_password_hash(password)
        
        # Dùng raw SQL INSERT để tránh conflict với trigger (OUTPUT clause)
        # SQL Server không cho phép OUTPUT clause khi có trigger enabled
        db.session.execute(
            db.text("""
                INSERT INTO Users (username, email, password_hash, full_name, phone_number, address, 
                                 role_id, member_level_id, is_active, is_locked, created_at, updated_at)
                VALUES (:username, :email, :password_hash, :full_name, :phone_number, :address, 
                        :role_id, :member_level_id, 1, 0, GETDATE(), GETDATE())
            """),
            {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'full_name': full_name,
                'phone_number': phone_number,
                'address': address,
                'role_id': role.role_id,
                'member_level_id': member_level_id
            }
        )
        db.session.commit()
        
        # Query lại user vừa tạo để lấy thông tin đầy đủ (bao gồm user_id)
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Đăng ký thất bại: Không thể tạo user'}), 500

        return jsonify({'message': 'Đăng ký thành công', 'user': user.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """API đăng nhập"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email và password là bắt buộc'}), 400
        
        # Tìm user theo email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'Email hoặc password không đúng'}), 401
        
        # Kiểm tra password
        if not user.check_password(password):
            return jsonify({'error': 'Email hoặc password không đúng'}), 401
        
        # Kiểm tra user có active không
        if not user.is_active:
            return jsonify({'error': 'Tài khoản đã bị khóa'}), 403
        
        # Kiểm tra user có bị lock không
        if user.is_locked:
            return jsonify({'error': 'Tài khoản đã bị khóa'}), 403
        
        # Cập nhật last_login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Tạo JWT token
        access_token = create_access_token(
            identity=str(user.user_id),  # Identity buộc phải là string trong phiên bản mới
            additional_claims={'role': user.role.role_name}
        )
        
        print(f"Token created for user_id: {user.user_id}, role: {user.role.role_name}")
        print(f"Token length: {len(access_token)}")
        
        return jsonify({
            'access_token': access_token,
            'role': user.role.role_name,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Lấy thông tin user hiện tại"""
    try:
        from flask_jwt_extended import get_jwt
        jwt_data = get_jwt()
        print(f"JWT Data: {jwt_data}")
        
        user_id = get_jwt_identity()
        print(f"User ID from token: {user_id}")
        
        # Convert back to int for lookup
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User không tồn tại'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Đăng xuất (Frontend sẽ xóa token khỏi localStorage)"""
    return jsonify({'message': 'Đăng xuất thành công'}), 200
