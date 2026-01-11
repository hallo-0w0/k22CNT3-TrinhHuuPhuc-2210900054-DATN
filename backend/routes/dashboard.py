"""
Dashboard Routes - Statistics
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.user import User
from models.order import Order
from models.invoice import Invoice
from models.review import Review
from models.member_level import MemberLevel
from utils.decorators import admin_required
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_dashboard_stats():
    """Lấy thống kê tổng quan (ADMIN only)"""
    try:
        # Tổng số users theo role
        from models.role import Role
        users_by_role = db.session.query(
            Role.role_name,
            func.count(User.user_id).label('count')
        ).join(User).group_by(Role.role_name).all()
        
        # Tổng số orders theo status
        from models.order_status import OrderStatus
        orders_by_status = db.session.query(
            OrderStatus.status_name,
            func.count(Order.order_id).label('count')
        ).join(Order).group_by(OrderStatus.status_name).all()
        
        # Tổng doanh thu
        total_revenue = db.session.query(func.sum(Invoice.total_amount)).scalar() or 0
        
        # Doanh thu tháng này
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        revenue_this_month = db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.invoice_date >= current_month_start
        ).scalar() or 0
        
        # Tổng số reviews và rating trung bình
        avg_rating = db.session.query(func.avg(Review.rating)).filter(
            Review.is_public == True,
            Review.is_verified == True
        ).scalar() or 0
        
        total_reviews = Review.query.filter_by(is_public=True, is_verified=True).count()
        
        # Users theo member level
        users_by_member_level = db.session.query(
            MemberLevel.level_name,
            func.count(User.user_id).label('count')
        ).join(User).group_by(MemberLevel.level_name).all()
        
        return jsonify({
            'users_by_role': {role: count for role, count in users_by_role},
            'orders_by_status': {status: count for status, count in orders_by_status},
            'total_revenue': float(total_revenue),
            'revenue_this_month': float(revenue_this_month),
            'average_rating': float(avg_rating),
            'total_reviews': total_reviews,
            'users_by_member_level': {level: count for level, count in users_by_member_level}
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy thống kê',
            'error': str(e)
        }), 500
