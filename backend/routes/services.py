"""
Services Routes - CRUD
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from models.service import Service
from models.service_category import ServiceCategory
from utils.decorators import roles_required
from utils.helpers import create_activity_log, paginate_query

services_bp = Blueprint('services', __name__)

@services_bp.route('', methods=['GET'])
def get_services():
    """Lấy danh sách services (public)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category_id = request.args.get('category_id', type=int)
        is_active = request.args.get('is_active', type=bool)
        search = request.args.get('search')
        
        query = Service.query
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        if search:
            query = query.filter(
                db.or_(
                    Service.service_name.like(f'%{search}%'),
                    Service.service_description.like(f'%{search}%')
                )
            )
        
        result = paginate_query(query.order_by(Service.display_order, Service.service_name), page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy danh sách services',
            'error': str(e)
        }), 500

@services_bp.route('/<int:service_id>', methods=['GET'])
def get_service(service_id):
    """Lấy chi tiết service (public)"""
    try:
        service = Service.query.get_or_404(service_id)
        return jsonify({
            'service': service.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy thông tin service',
            'error': str(e)
        }), 500

@services_bp.route('', methods=['POST'])
@jwt_required()
@roles_required('ADMIN')
def create_service():
    """Tạo service mới (ADMIN only)"""
    try:
        data = request.get_json()
        
        required_fields = ['service_name', 'category_id', 'base_price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'message': f'Thiếu trường {field}',
                    'error': 'missing_field'
                }), 400
        
        # Check category exists
        category = ServiceCategory.query.get(data['category_id'])
        if not category:
            return jsonify({
                'message': 'Category không tồn tại',
                'error': 'category_not_found'
            }), 404
        
        service = Service(
            service_name=data['service_name'],
            service_description=data.get('service_description'),
            category_id=data['category_id'],
            base_price=data['base_price'],
            duration_hours=data.get('duration_hours'),
            unit=data.get('unit'),
            is_active=data.get('is_active', True),
            display_order=data.get('display_order', 0)
        )
        
        db.session.add(service)
        db.session.commit()
        
        # Activity log
        current_user_id = get_jwt_identity()
        create_activity_log(current_user_id, 'CREATE', 'Service', service.service_id, f'Tạo service: {service.service_name}')
        
        return jsonify({
            'message': 'Tạo service thành công',
            'service': service.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi tạo service',
            'error': str(e)
        }), 500

@services_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
@roles_required('ADMIN')
def update_service(service_id):
    """Cập nhật service (ADMIN only)"""
    try:
        service = Service.query.get_or_404(service_id)
        data = request.get_json()
        
        if 'service_name' in data:
            service.service_name = data['service_name']
        if 'service_description' in data:
            service.service_description = data.get('service_description')
        if 'category_id' in data:
            category = ServiceCategory.query.get(data['category_id'])
            if not category:
                return jsonify({
                    'message': 'Category không tồn tại',
                    'error': 'category_not_found'
                }), 404
            service.category_id = data['category_id']
        if 'base_price' in data:
            service.base_price = data['base_price']
        if 'duration_hours' in data:
            service.duration_hours = data.get('duration_hours')
        if 'unit' in data:
            service.unit = data.get('unit')
        if 'is_active' in data:
            service.is_active = data['is_active']
        if 'display_order' in data:
            service.display_order = data.get('display_order', 0)
        
        db.session.commit()
        
        # Activity log
        current_user_id = get_jwt_identity()
        create_activity_log(current_user_id, 'UPDATE', 'Service', service.service_id, f'Cập nhật service: {service.service_name}')
        
        return jsonify({
            'message': 'Cập nhật service thành công',
            'service': service.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi cập nhật service',
            'error': str(e)
        }), 500

@services_bp.route('/<int:service_id>', methods=['DELETE'])
@jwt_required()
@roles_required('ADMIN')
def delete_service(service_id):
    """Xóa service (ADMIN only)"""
    try:
        service = Service.query.get_or_404(service_id)
        service_name = service.service_name
        
        db.session.delete(service)
        db.session.commit()
        
        # Activity log
        current_user_id = get_jwt_identity()
        create_activity_log(current_user_id, 'DELETE', 'Service', service_id, f'Xóa service: {service_name}')
        
        return jsonify({
            'message': 'Xóa service thành công'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi xóa service',
            'error': str(e)
        }), 500
