from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import db
from backend.models.content import Content

content_bp = Blueprint('content', __name__)

@content_bp.route('/<content_type>', methods=['GET'])
def get_content(content_type):
    """Lấy nội dung theo type (public)"""
    try:
        contents = Content.query.filter_by(
            content_type=content_type.upper(),
            is_active=True
        ).order_by(Content.display_order, Content.created_at.desc()).all()
        
        if not contents:
            return jsonify({'error': 'Không tìm thấy nội dung'}), 404
        
        # Nếu chỉ có 1, trả về object, nếu nhiều trả về array
        if len(contents) == 1:
            return jsonify(contents[0].to_dict()), 200
        else:
            return jsonify([c.to_dict() for c in contents]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
