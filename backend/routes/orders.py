"""
Orders Routes - CRUD
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.order import Order
from models.service import Service
from models.user import User
from models.order_status import OrderStatus
from models.order_status_history import OrderStatusHistory
from utils.decorators import roles_required
from utils.helpers import create_activity_log, paginate_query, calculate_discount_price, calculate_member_level_priority
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """Lấy danh sách orders"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_id = request.args.get('status_id', type=int)
        customer_id = request.args.get('customer_id', type=int)
        
        query = Order.query
        
        # CUSTOMER chỉ xem đơn của mình
        if current_user.is_customer():
            query = query.filter_by(customer_id=current_user_id)
        # STAFF chỉ xem đơn được phân công
        elif current_user.is_staff():
            from models.order_assignment import OrderAssignment
            assigned_order_ids = db.session.query(OrderAssignment.order_id).filter_by(
                staff_id=current_user_id,
                is_active=True
            ).subquery()
            query = query.filter(Order.order_id.in_(db.session.query(assigned_order_ids.c.order_id)))
        # ADMIN xem tất cả, có thể filter theo customer_id
        
        if status_id:
            query = query.filter_by(status_id=status_id)
        
        if customer_id and current_user.is_admin():
            query = query.filter_by(customer_id=customer_id)
        
        result = paginate_query(query.order_by(Order.priority.desc(), Order.order_date.desc()), page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy danh sách orders',
            'error': str(e)
        }), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Lấy chi tiết order"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        order = Order.query.get_or_404(order_id)
        
        # Kiểm tra quyền
        if current_user.is_customer() and order.customer_id != current_user_id:
            return jsonify({
                'message': 'Không có quyền xem đơn này',
                'error': 'insufficient_permissions'
            }), 403
        
        if current_user.is_staff():
            from models.order_assignment import OrderAssignment
            assignment = OrderAssignment.query.filter_by(
                order_id=order_id,
                staff_id=current_user_id,
                is_active=True
            ).first()
            if not assignment and not current_user.is_admin():
                return jsonify({
                    'message': 'Không có quyền xem đơn này',
                    'error': 'insufficient_permissions'
                }), 403
        
        return jsonify({
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy thông tin order',
            'error': str(e)
        }), 500

@orders_bp.route('', methods=['POST'])
@jwt_required()
@roles_required('CUSTOMER')
def create_order():
    """Tạo order mới (CUSTOMER only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        data = request.get_json()
        
        required_fields = ['service_id', 'scheduled_date', 'service_address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'message': f'Thiếu trường {field}',
                    'error': 'missing_field'
                }), 400
        
        # Check service exists
        service = Service.query.get(data['service_id'])
        if not service or not service.is_active:
            return jsonify({
                'message': 'Service không tồn tại hoặc không hoạt động',
                'error': 'service_not_found'
            }), 404
        
        # Calculate price với member level discount
        unit_price = float(service.base_price)
        quantity = float(data.get('quantity', 1))
        discount_percentage, discount_amount, final_price = calculate_discount_price(
            unit_price * quantity,
            current_user.member_level
        )
        
        # Calculate priority
        priority = calculate_member_level_priority(
            current_user.member_level.level_code if current_user.member_level else 'SILVER'
        )
        
        # Create order
        order = Order(
            order_code=Order.generate_order_code(),
            customer_id=current_user_id,
            service_id=data['service_id'],
            scheduled_date=datetime.fromisoformat(data['scheduled_date'].replace('Z', '+00:00')),
            scheduled_time=datetime.strptime(data['scheduled_time'], '%H:%M:%S').time() if data.get('scheduled_time') else None,
            service_address=data['service_address'],
            quantity=quantity,
            unit_price=unit_price,
            discount_percentage=discount_percentage,
            discount_amount=discount_amount,
            total_amount=final_price,
            notes=data.get('notes'),
            priority=priority
        )
        
        db.session.add(order)
        db.session.commit()
        
        # Create status history
        status_history = OrderStatusHistory(
            order_id=order.order_id,
            old_status_id=None,
            new_status_id=order.status_id,
            changed_by=current_user_id,
            change_reason='Khách hàng tạo đơn'
        )
        db.session.add(status_history)
        db.session.commit()
        
        # Activity log
        create_activity_log(current_user_id, 'CREATE', 'Order', order.order_id, f'Tạo đơn: {order.order_code}')
        
        return jsonify({
            'message': 'Tạo đơn thành công',
            'order': order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi tạo đơn',
            'error': str(e)
        }), 500

@orders_bp.route('/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    """Cập nhật order"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        # Kiểm tra quyền
        can_update = False
        if current_user.is_admin():
            can_update = True
        elif current_user.is_customer() and order.customer_id == current_user_id:
            # CUSTOMER chỉ có thể sửa đơn ở trạng thái PENDING
            pending_status = OrderStatus.query.filter_by(status_code='PENDING').first()
            if order.status_id == pending_status.status_id:
                can_update = True
        
        if not can_update:
            return jsonify({
                'message': 'Không có quyền sửa đơn này',
                'error': 'insufficient_permissions'
            }), 403
        
        # Update fields
        if 'scheduled_date' in data:
            order.scheduled_date = datetime.fromisoformat(data['scheduled_date'].replace('Z', '+00:00'))
        if 'scheduled_time' in data:
            order.scheduled_time = datetime.strptime(data['scheduled_time'], '%H:%M:%S').time() if data['scheduled_time'] else None
        if 'service_address' in data:
            order.service_address = data['service_address']
        if 'notes' in data:
            order.notes = data.get('notes')
        if 'quantity' in data:
            order.quantity = data['quantity']
            # Recalculate total
            order.calculate_total()
        
        # Chỉ ADMIN mới được sửa status
        if 'status_id' in data and current_user.is_admin():
            new_status_id = data['status_id']
            new_status = OrderStatus.query.get(new_status_id)
            if not new_status:
                return jsonify({
                    'message': 'Status không tồn tại',
                    'error': 'status_not_found'
                }), 404
            
            # Create status history
            status_history = OrderStatusHistory(
                order_id=order.order_id,
                old_status_id=order.status_id,
                new_status_id=new_status_id,
                changed_by=current_user_id,
                change_reason=data.get('change_reason', 'Admin cập nhật trạng thái')
            )
            db.session.add(status_history)
            order.status_id = new_status_id
        
        db.session.commit()
        
        # Activity log
        create_activity_log(current_user_id, 'UPDATE', 'Order', order.order_id, f'Cập nhật đơn: {order.order_code}')
        
        return jsonify({
            'message': 'Cập nhật đơn thành công',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi cập nhật đơn',
            'error': str(e)
        }), 500

@orders_bp.route('/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    """Xóa order (chỉ CUSTOMER có thể hủy đơn PENDING)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        order = Order.query.get_or_404(order_id)
        
        # Kiểm tra quyền
        can_delete = False
        if current_user.is_admin():
            can_delete = True
        elif current_user.is_customer() and order.customer_id == current_user_id:
            # CUSTOMER chỉ có thể hủy đơn ở trạng thái PENDING
            pending_status = OrderStatus.query.filter_by(status_code='PENDING').first()
            if order.status_id == pending_status.status_id:
                can_delete = True
        
        if not can_delete:
            return jsonify({
                'message': 'Không thể hủy đơn này',
                'error': 'cannot_cancel_order'
            }), 403
        
        # Update status to CANCELLED instead of delete
        cancelled_status = OrderStatus.query.filter_by(status_code='CANCELLED').first()
        if cancelled_status:
            order.status_id = cancelled_status.status_id
            
            # Create status history
            status_history = OrderStatusHistory(
                order_id=order.order_id,
                old_status_id=order.status_id,
                new_status_id=cancelled_status.status_id,
                changed_by=current_user_id,
                change_reason='Hủy đơn'
            )
            db.session.add(status_history)
            db.session.commit()
            
            # Activity log
            create_activity_log(current_user_id, 'UPDATE', 'Order', order.order_id, f'Hủy đơn: {order.order_code}')
            
            return jsonify({
                'message': 'Hủy đơn thành công',
                'order': order.to_dict()
            }), 200
        else:
            return jsonify({
                'message': 'Không tìm thấy trạng thái CANCELLED',
                'error': 'status_not_found'
            }), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi hủy đơn',
            'error': str(e)
        }), 500
