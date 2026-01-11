"""
Member Levels Routes - CRUD
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from models.member_level import MemberLevel
from utils.decorators import admin_required
from utils.helpers import create_activity_log, paginate_query

member_levels_bp = Blueprint('member_levels', __name__)

@member_levels_bp.route('', methods=['GET'])
def get_member_levels():
    """Lấy danh sách member levels (public)"""
    try:
        levels = MemberLevel.query.filter_by(is_active=True).order_by(MemberLevel.discount_percentage).all()
        return jsonify({
            'member_levels': [level.to_dict() for level in levels]
        }), 200
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy danh sách member levels',
            'error': str(e)
        }), 500

@member_levels_bp.route('/<int:member_level_id>', methods=['GET'])
def get_member_level(member_level_id):
    """Lấy chi tiết member level (public)"""
    try:
        level = MemberLevel.query.get_or_404(member_level_id)
        return jsonify({
            'member_level': level.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy thông tin member level',
            'error': str(e)
        }), 500

@member_levels_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_member_level():
    """Tạo member level (ADMIN only)"""
    try:
        data = request.get_json()
        
        required_fields = ['level_code', 'level_name', 'discount_percentage']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'message': f'Thiếu trường {field}',
                    'error': 'missing_field'
                }), 400
        
        # Check level_code unique
        if MemberLevel.query.filter_by(level_code=data['level_code']).first():
            return jsonify({
                'message': 'Level code đã tồn tại',
                'error': 'level_code_exists'
            }), 400
        
        level = MemberLevel(
            level_code=data['level_code'],
            level_name=data['level_name'],
            discount_percentage=data['discount_percentage'],
            min_total_amount=data.get('min_total_amount'),
            min_service_count=data.get('min_service_count'),
            min_continuous_months=data.get('min_continuous_months'),
            description=data.get('description'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(level)
        db.session.commit()
        
        # Activity log
        current_user_id = get_jwt_identity()
        create_activity_log(current_user_id, 'CREATE', 'MemberLevel', level.member_level_id, f'Tạo member level: {level.level_code}')
        
        return jsonify({
            'message': 'Tạo member level thành công',
            'member_level': level.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi tạo member level',
            'error': str(e)
        }), 500

@member_levels_bp.route('/<int:member_level_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_member_level(member_level_id):
    """Cập nhật member level (ADMIN only)"""
    try:
        level = MemberLevel.query.get_or_404(member_level_id)
        data = request.get_json()
        
        if 'level_name' in data:
            level.level_name = data['level_name']
        if 'discount_percentage' in data:
            level.discount_percentage = data['discount_percentage']
        if 'min_total_amount' in data:
            level.min_total_amount = data.get('min_total_amount')
        if 'min_service_count' in data:
            level.min_service_count = data.get('min_service_count')
        if 'min_continuous_months' in data:
            level.min_continuous_months = data.get('min_continuous_months')
        if 'description' in data:
            level.description = data.get('description')
        if 'is_active' in data:
            level.is_active = data['is_active']
        
        db.session.commit()
        
        # Activity log
        current_user_id = get_jwt_identity()
        create_activity_log(current_user_id, 'UPDATE', 'MemberLevel', level.member_level_id, f'Cập nhật member level: {level.level_code}')
        
        return jsonify({
            'message': 'Cập nhật member level thành công',
            'member_level': level.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi cập nhật member level',
            'error': str(e)
        }), 500

@member_levels_bp.route('/<int:member_level_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_member_level(member_level_id):
    """Xóa member level (ADMIN only)"""
    try:
        level = MemberLevel.query.get_or_404(member_level_id)
        level_code = level.level_code
        
        # Check if any users are using this level
        from models.user import User
        users_count = User.query.filter_by(member_level_id=member_level_id).count()
        if users_count > 0:
            return jsonify({
                'message': f'Không thể xóa member level này vì có {users_count} người dùng đang sử dụng',
                'error': 'level_in_use'
            }), 400
        
        db.session.delete(level)
        db.session.commit()
        
        # Activity log
        current_user_id = get_jwt_identity()
        create_activity_log(current_user_id, 'DELETE', 'MemberLevel', member_level_id, f'Xóa member level: {level_code}')
        
        return jsonify({
            'message': 'Xóa member level thành công'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi xóa member level',
            'error': str(e)
        }), 500
