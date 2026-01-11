"""
Reviews Routes - CRUD
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.review import Review
from models.order import Order
from models.order_status import OrderStatus
from models.user import User
from utils.decorators import roles_required
from utils.helpers import create_activity_log, paginate_query
from datetime import datetime

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('', methods=['GET'])
def get_reviews():
    """Lấy danh sách reviews (public, chỉ reviews công khai)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        service_id = request.args.get('service_id', type=int)
        min_rating = request.args.get('min_rating', type=int)
        
        query = Review.query.filter_by(is_public=True, is_verified=True)
        
        if service_id:
            query = query.join(Order).filter(Order.service_id == service_id)
        
        if min_rating:
            query = query.filter(Review.rating >= min_rating)
        
        result = paginate_query(query.order_by(Review.created_at.desc()), page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy danh sách reviews',
            'error': str(e)
        }), 500

@reviews_bp.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """Lấy chi tiết review"""
    try:
        review = Review.query.get_or_404(review_id)
        return jsonify({
            'review': review.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy thông tin review',
            'error': str(e)
        }), 500

@reviews_bp.route('', methods=['POST'])
@jwt_required()
@roles_required('CUSTOMER')
def create_review():
    """Tạo review (CUSTOMER only, chỉ sau khi đơn COMPLETED)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['order_id', 'rating']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'message': f'Thiếu trường {field}',
                    'error': 'missing_field'
                }), 400
        
        # Check order exists and belongs to user
        order = Order.query.get(data['order_id'])
        if not order:
            return jsonify({
                'message': 'Đơn hàng không tồn tại',
                'error': 'order_not_found'
            }), 404
        
        if order.customer_id != current_user_id:
            return jsonify({
                'message': 'Không có quyền đánh giá đơn này',
                'error': 'insufficient_permissions'
            }), 403
        
        # Check order is completed
        completed_status = OrderStatus.query.filter_by(status_code='COMPLETED').first()
        if order.status_id != completed_status.status_id:
            return jsonify({
                'message': 'Chỉ có thể đánh giá đơn đã hoàn thành',
                'error': 'order_not_completed'
            }), 400
        
        # Check review already exists
        if Review.query.filter_by(order_id=order.order_id).first():
            return jsonify({
                'message': 'Đơn này đã được đánh giá',
                'error': 'review_exists'
            }), 400
        
        # Validate rating
        rating = data['rating']
        if rating < 1 or rating > 5:
            return jsonify({
                'message': 'Rating phải từ 1 đến 5',
                'error': 'invalid_rating'
            }), 400
        
        review = Review(
            order_id=order.order_id,
            customer_id=current_user_id,
            rating=rating,
            review_text=data.get('review_text'),
            is_public=data.get('is_public', True),
            is_verified=True
        )
        
        db.session.add(review)
        db.session.commit()
        
        # Activity log
        create_activity_log(current_user_id, 'CREATE', 'Review', review.review_id, f'Tạo review cho đơn: {order.order_code}')
        
        return jsonify({
            'message': 'Tạo review thành công',
            'review': review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi tạo review',
            'error': str(e)
        }), 500

@reviews_bp.route('/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """Cập nhật review"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        review = Review.query.get_or_404(review_id)
        data = request.get_json()
        
        # Kiểm tra quyền: chỉ CUSTOMER sở hữu hoặc ADMIN
        can_update = False
        if current_user.is_admin():
            can_update = True
        elif current_user.is_customer() and review.customer_id == current_user_id:
            can_update = True
        
        if not can_update:
            return jsonify({
                'message': 'Không có quyền sửa review này',
                'error': 'insufficient_permissions'
            }), 403
        
        if 'rating' in data:
            rating = data['rating']
            if rating < 1 or rating > 5:
                return jsonify({
                    'message': 'Rating phải từ 1 đến 5',
                    'error': 'invalid_rating'
                }), 400
            review.rating = rating
        
        if 'review_text' in data:
            review.review_text = data.get('review_text')
        
        if 'is_public' in data and current_user.is_customer():
            review.is_public = data['is_public']
        
        # ADMIN có thể thêm response
        if 'admin_response' in data and current_user.is_admin():
            review.admin_response = data.get('admin_response')
            review.admin_response_by = current_user_id
            review.admin_response_at = datetime.utcnow()
        
        db.session.commit()
        
        # Activity log
        create_activity_log(current_user_id, 'UPDATE', 'Review', review.review_id, f'Cập nhật review')
        
        return jsonify({
            'message': 'Cập nhật review thành công',
            'review': review.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi cập nhật review',
            'error': str(e)
        }), 500

@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
@roles_required('ADMIN')
def delete_review(review_id):
    """Xóa review (ADMIN only)"""
    try:
        review = Review.query.get_or_404(review_id)
        db.session.delete(review)
        db.session.commit()
        
        # Activity log
        current_user_id = get_jwt_identity()
        create_activity_log(current_user_id, 'DELETE', 'Review', review_id, 'Xóa review')
        
        return jsonify({
            'message': 'Xóa review thành công'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi xóa review',
            'error': str(e)
        }), 500
