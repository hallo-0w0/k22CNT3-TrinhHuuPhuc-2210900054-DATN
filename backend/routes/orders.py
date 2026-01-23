from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import db
from backend.models.order import Order, OrderStatus, OrderProgress, OrderStatusHistory
from backend.models.user import User, MemberLevel
from backend.models.service import Service
from datetime import datetime
import uuid

orders_bp = Blueprint('orders', __name__)

def check_member_level_upgrade(customer_id):
    """Kiểm tra và nâng cấp member level cho customer"""
    try:
        customer = User.query.get(customer_id)
        if not customer or customer.role.role_name != 'CUSTOMER':
            return
        
        # Tính toán từ bảng Orders
        completed_orders = Order.query.filter_by(
            customer_id=customer_id,
            status_id=OrderStatus.query.filter_by(status_code='COMPLETED').first().status_id
        ).all()
        
        service_count = len(completed_orders)
        total_spent = sum(float(order.total_amount) for order in completed_orders)
        
        # Tính continuous_months (đơn giản: số tháng có đơn COMPLETED)
        if completed_orders:
            months = set()
            for order in completed_orders:
                if order.order_date:
                    months.add((order.order_date.year, order.order_date.month))
            continuous_months = len(months)
        else:
            continuous_months = 0
        
        # Kiểm tra điều kiện nâng cấp
        member_levels = MemberLevel.query.filter_by(is_active=True).order_by(
            MemberLevel.member_level_id
        ).all()
        
        new_level = None
        for level in member_levels:
            if (level.min_total_amount and total_spent >= float(level.min_total_amount)) and \
               (level.min_service_count and service_count >= level.min_service_count) and \
               (level.min_continuous_months and continuous_months >= level.min_continuous_months):
                new_level = level
        
        # Nâng cấp nếu đủ điều kiện
        if new_level and (not customer.member_level_id or new_level.member_level_id > customer.member_level_id):
            customer.member_level_id = new_level.member_level_id
            db.session.commit()
            
    except Exception as e:
        print(f"Error checking member level upgrade: {e}")

@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """Lấy danh sách đơn hàng"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        query = Order.query
        
        # Filter theo role
        if user.role.role_name == 'CUSTOMER':
            query = query.filter_by(customer_id=user_id)
        elif user.role.role_name == 'STAFF':
            # Lấy các đơn được phân công cho staff này
            from backend.models.order import OrderAssignment
            assigned_order_ids = db.session.query(OrderAssignment.order_id)\
                .filter_by(staff_id=user_id, is_active=True).all()
            query = query.filter(Order.order_id.in_([oid[0] for oid in assigned_order_ids]))
        # ADMIN xem tất cả
        
        status_id = request.args.get('status_id', type=int)
        if status_id:
            query = query.filter_by(status_id=status_id)
        
        orders = query.order_by(Order.created_at.desc()).all()
        
        return jsonify([order.to_dict() for order in orders]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """Tạo đơn hàng mới (CUSTOMER only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role.role_name != 'CUSTOMER':
            return jsonify({'error': 'Chỉ khách hàng mới có thể tạo đơn'}), 403
        
        data = request.get_json()
        
        # Validate
        service_id = data.get('service_id')
        scheduled_date = data.get('scheduled_date')
        service_address = data.get('service_address')
        quantity = data.get('quantity', 1)
        
        if not all([service_id, scheduled_date, service_address]):
            return jsonify({'error': 'Thiếu thông tin bắt buộc'}), 400
        
        # Lấy service
        service = Service.query.get_or_404(service_id)
        if not service.is_active:
            return jsonify({'error': 'Dịch vụ không khả dụng'}), 400
        
        # Lấy member level và discount
        discount_percentage = 0
        if user.member_level:
            discount_percentage = float(user.member_level.discount_percentage)
        
        # Tính toán giá
        unit_price = float(service.base_price)
        subtotal = unit_price * float(quantity)
        discount_amount = subtotal * (discount_percentage / 100)
        total_amount = subtotal - discount_amount
        
        # Tạo order code
        order_code = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Tạo order
        order = Order(
            order_code=order_code,
            customer_id=user_id,
            service_id=service_id,
            scheduled_date=datetime.fromisoformat(scheduled_date.replace('Z', '+00:00')),
            scheduled_time=datetime.strptime(data.get('scheduled_time', '09:00'), '%H:%M').time() if data.get('scheduled_time') else None,
            service_address=service_address,
            quantity=quantity,
            unit_price=unit_price,
            discount_percentage=discount_percentage,
            discount_amount=discount_amount,
            total_amount=total_amount,
            notes=data.get('notes'),
            status_id=OrderStatus.query.filter_by(status_code='PENDING').first().status_id,
            priority=user.member_level.member_level_id if user.member_level else 0
        )
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify(order.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Lấy chi tiết đơn hàng"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        order = Order.query.get_or_404(order_id)
        
        # Kiểm tra quyền truy cập
        if user.role.role_name == 'CUSTOMER' and order.customer_id != user_id:
            return jsonify({'error': 'Không có quyền truy cập'}), 403
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """Cập nhật trạng thái đơn hàng (ADMIN/STAFF)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role.role_name not in ['ADMIN', 'STAFF']:
            return jsonify({'error': 'Không có quyền'}), 403
        
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        status_code = data.get('status_code')
        
        if not status_code:
            return jsonify({'error': 'Thiếu status_code'}), 400
        
        new_status = OrderStatus.query.filter_by(status_code=status_code).first()
        if not new_status:
            return jsonify({'error': 'Trạng thái không hợp lệ'}), 400
        
        # Lưu lịch sử
        history = OrderStatusHistory(
            order_id=order_id,
            old_status_id=order.status_id,
            new_status_id=new_status.status_id,
            changed_by=user_id,
            change_reason=data.get('reason')
        )
        db.session.add(history)
        
        # Cập nhật trạng thái
        old_status_code = order.status.status_code
        order.status_id = new_status.status_id
        order.updated_at = datetime.utcnow()
        
        # Nếu chuyển sang COMPLETED, kiểm tra nâng cấp member level
        if new_status.status_code == 'COMPLETED' and old_status_code != 'COMPLETED':
            check_member_level_upgrade(order.customer_id)
        
        db.session.commit()
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/progress', methods=['POST'])
@jwt_required()
def add_progress(order_id):
    """Thêm tiến độ đơn hàng (STAFF)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role.role_name != 'STAFF':
            return jsonify({'error': 'Chỉ nhân viên mới có thể thêm tiến độ'}), 403
        
        order = Order.query.get_or_404(order_id)
        
        # Kiểm tra staff có được phân công không
        from backend.models.order import OrderAssignment
        assignment = OrderAssignment.query.filter_by(
            order_id=order_id,
            staff_id=user_id,
            is_active=True
        ).first()
        
        if not assignment and user.role.role_name != 'ADMIN':
            return jsonify({'error': 'Bạn không được phân công đơn này'}), 403
        
        data = request.get_json()
        
        progress = OrderProgress(
            order_id=order_id,
            staff_id=user_id,
            progress_note=data.get('progress_note'),
            issue_report=data.get('issue_report')
        )
        
        if data.get('image_urls'):
            progress.set_image_urls(data.get('image_urls'))
        
        db.session.add(progress)
        db.session.commit()
        
        return jsonify(progress.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/progress', methods=['GET'])
@jwt_required()
def get_progress(order_id):
    """Lấy tiến độ đơn hàng"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        order = Order.query.get_or_404(order_id)
        
        # Kiểm tra quyền
        if user.role.role_name == 'CUSTOMER' and order.customer_id != user_id:
            return jsonify({'error': 'Không có quyền truy cập'}), 403
        
        progress_records = OrderProgress.query.filter_by(order_id=order_id)\
            .order_by(OrderProgress.created_at.desc()).all()
        
        return jsonify([p.to_dict() for p in progress_records]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
