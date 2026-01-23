from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import db
from backend.models.service import Service, ServiceCategory

services_bp = Blueprint('services', __name__)

@services_bp.route('', methods=['GET'])
def get_services():
    """Lấy danh sách dịch vụ (public)"""
    try:
        category_id = request.args.get('category_id', type=int)
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        
        query = Service.query
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if is_active:
            query = query.filter_by(is_active=True)
        
        services = query.order_by(Service.display_order, Service.service_name).all()
        
        return jsonify([service.to_dict() for service in services]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@services_bp.route('/<int:service_id>', methods=['GET'])
def get_service(service_id):
    """Lấy chi tiết dịch vụ"""
    try:
        service = Service.query.get_or_404(service_id)
        return jsonify(service.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@services_bp.route('/categories', methods=['GET'])
def get_categories():
    """Lấy danh sách danh mục dịch vụ"""
    try:
        categories = ServiceCategory.query.filter_by(is_active=True)\
            .order_by(ServiceCategory.display_order, ServiceCategory.category_name).all()
        
        return jsonify([cat.to_dict() for cat in categories]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
