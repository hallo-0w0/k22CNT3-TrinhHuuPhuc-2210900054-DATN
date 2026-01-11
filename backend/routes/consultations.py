"""
Consultations Routes - CRUD
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.consultation import Consultation
from models.user import User
from utils.decorators import roles_required
from utils.helpers import create_activity_log, paginate_query
from datetime import datetime

consultations_bp = Blueprint('consultations', __name__)

@consultations_bp.route('', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def get_consultations():
    """Lấy danh sách consultations (ADMIN only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        query = Consultation.query
        
        if status:
            query = query.filter_by(status=status)
        
        result = paginate_query(query.order_by(Consultation.created_at.desc()), page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy danh sách consultations',
            'error': str(e)
        }), 500

@consultations_bp.route('/<int:consultation_id>', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def get_consultation(consultation_id):
    """Lấy chi tiết consultation (ADMIN only)"""
    try:
        consultation = Consultation.query.get_or_404(consultation_id)
        return jsonify({
            'consultation': consultation.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy thông tin consultation',
            'error': str(e)
        }), 500

@consultations_bp.route('', methods=['POST'])
def create_consultation():
    """Tạo consultation (public, không cần đăng nhập)"""
    try:
        data = request.get_json()
        
        required_fields = ['full_name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'message': f'Thiếu trường {field}',
                    'error': 'missing_field'
                }), 400
        
        consultation = Consultation(
            full_name=data['full_name'],
            email=data['email'],
            phone_number=data.get('phone_number'),
            company_name=data.get('company_name'),
            address=data.get('address'),
            service_interest=data.get('service_interest'),
            message=data['message'],
            status='PENDING'
        )
        
        db.session.add(consultation)
        db.session.commit()
        
        return jsonify({
            'message': 'Gửi yêu cầu tư vấn thành công',
            'consultation': consultation.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi gửi yêu cầu tư vấn',
            'error': str(e)
        }), 500

@consultations_bp.route('/<int:consultation_id>', methods=['PUT'])
@jwt_required()
@roles_required('ADMIN')
def update_consultation(consultation_id):
    """Cập nhật consultation (ADMIN only)"""
    try:
        consultation = Consultation.query.get_or_404(consultation_id)
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        if 'status' in data:
            consultation.status = data['status']
        
        if 'response_message' in data:
            consultation.response_message = data.get('response_message')
            consultation.handled_by = current_user_id
            consultation.handled_at = datetime.utcnow()
        
        db.session.commit()
        
        # Activity log
        create_activity_log(current_user_id, 'UPDATE', 'Consultation', consultation.consultation_id, f'Xử lý consultation: {consultation.full_name}')
        
        return jsonify({
            'message': 'Cập nhật consultation thành công',
            'consultation': consultation.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi cập nhật consultation',
            'error': str(e)
        }), 500

@consultations_bp.route('/<int:consultation_id>', methods=['DELETE'])
@jwt_required()
@roles_required('ADMIN')
def delete_consultation(consultation_id):
    """Xóa consultation (ADMIN only)"""
    try:
        consultation = Consultation.query.get_or_404(consultation_id)
        db.session.delete(consultation)
        db.session.commit()
        
        # Activity log
        current_user_id = get_jwt_identity()
        create_activity_log(current_user_id, 'DELETE', 'Consultation', consultation_id, 'Xóa consultation')
        
        return jsonify({
            'message': 'Xóa consultation thành công'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi xóa consultation',
            'error': str(e)
        }), 500
