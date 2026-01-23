"""
Staff Routes - Logic nghiệp vụ cho nhân viên
Chỉ staff được phân công mới có quyền thao tác
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import db
from backend.models.order import Order, OrderStatus, OrderProgress, OrderStatusHistory, OrderAssignment
from backend.models.user import User
from datetime import datetime

staff_bp = Blueprint('staff', __name__)

def check_staff_assignment(order_id, staff_id):
    """
    Kiểm tra staff có được phân công cho đơn hàng này không
    Returns: (is_assigned: bool, assignment: OrderAssignment)
    """
    assignment = OrderAssignment.query.filter_by(
        order_id=order_id,
        staff_id=staff_id,
        is_active=True
    ).first()
    
    return (assignment is not None, assignment)

# ==================== 1. LẤY DANH SÁCH ĐƠN ĐƯỢC PHÂN CÔNG ====================
@staff_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_assigned_orders():
    """
    Lấy danh sách đơn hàng được phân công cho staff hiện tại
    Không trả đơn CANCELLED
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Kiểm tra role
        if user.role.role_name != 'STAFF':
            return jsonify({'error': 'Chỉ nhân viên mới có quyền truy cập'}), 403
        
        # Lấy các order_id được phân công
        assigned_order_ids = db.session.query(OrderAssignment.order_id)\
            .filter_by(staff_id=user_id, is_active=True).all()
        
        order_ids = [oid[0] for oid in assigned_order_ids]
        
        if not order_ids:
            return jsonify([]), 200
        
        # Lấy orders, loại bỏ CANCELLED
        cancelled_status = OrderStatus.query.filter_by(status_code='CANCELLED').first()
        
        query = Order.query.filter(Order.order_id.in_(order_ids))
        
        if cancelled_status:
            query = query.filter(Order.status_id != cancelled_status.status_id)
        
        orders = query.order_by(Order.scheduled_date.asc()).all()
        
        return jsonify([order.to_dict() for order in orders]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 2. STAFF NHẬN VIỆC ====================
@staff_bp.route('/orders/<int:order_id>/start', methods=['PUT'])
@jwt_required()
def start_order(order_id):
    """
    Staff nhận việc - chuyển trạng thái từ CONFIRMED → IN_PROGRESS
    Điều kiện:
    - Staff được phân công
    - Trạng thái hiện tại = CONFIRMED
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Kiểm tra role
        if user.role.role_name != 'STAFF':
            return jsonify({'error': 'Chỉ nhân viên mới có quyền thao tác'}), 403
        
        # Kiểm tra đơn tồn tại
        order = Order.query.get_or_404(order_id)
        
        # Kiểm tra staff có được phân công không
        is_assigned, assignment = check_staff_assignment(order_id, user_id)
        if not is_assigned:
            return jsonify({'error': 'Bạn không được phân công cho đơn hàng này'}), 403
        
        # Kiểm tra trạng thái hiện tại
        if order.status.status_code != 'CONFIRMED':
            return jsonify({
                'error': f'Không thể nhận việc. Đơn hàng đang ở trạng thái: {order.status.status_name}'
            }), 400
        
        # Lấy trạng thái IN_PROGRESS
        in_progress_status = OrderStatus.query.filter_by(status_code='IN_PROGRESS').first()
        if not in_progress_status:
            return jsonify({'error': 'Lỗi hệ thống: Trạng thái IN_PROGRESS chưa được cấu hình'}), 500
        
        # ATOMIC: Cập nhật trạng thái + Ghi lịch sử
        old_status_id = order.status_id
        
        # Ghi lịch sử
        history = OrderStatusHistory(
            order_id=order_id,
            old_status_id=old_status_id,
            new_status_id=in_progress_status.status_id,
            changed_by=user_id,
            change_reason='Nhân viên bắt đầu thực hiện công việc'
        )
        db.session.add(history)
        
        # Cập nhật trạng thái
        order.status_id = in_progress_status.status_id
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Đã nhận việc thành công',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== 3. XEM CHI TIẾT ĐƠN ====================
@staff_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):
    """
    Xem chi tiết đơn hàng được phân công
    Bao gồm: thông tin đơn, khách hàng, dịch vụ, lịch sử, tiến độ
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Kiểm tra role
        if user.role.role_name != 'STAFF':
            return jsonify({'error': 'Chỉ nhân viên mới có quyền truy cập'}), 403
        
        # Kiểm tra đơn tồn tại
        order = Order.query.get_or_404(order_id)
        
        # Kiểm tra staff có được phân công không
        is_assigned, assignment = check_staff_assignment(order_id, user_id)
        if not is_assigned:
            return jsonify({'error': 'Bạn không có quyền xem đơn hàng này'}), 403
        
        # Lấy lịch sử tiến độ
        progress_records = OrderProgress.query.filter_by(order_id=order_id)\
            .order_by(OrderProgress.created_at.desc()).all()
        
        # Trả về đầy đủ thông tin
        order_dict = order.to_dict()
        order_dict['progress'] = [p.to_dict() for p in progress_records]
        
        return jsonify(order_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 4. CẬP NHẬT TIẾN ĐỘ ====================
@staff_bp.route('/orders/<int:order_id>/progress', methods=['POST'])
@jwt_required()
def add_order_progress(order_id):
    """
    Cập nhật tiến độ công việc
    Điều kiện:
    - Staff được phân công
    - Trạng thái = IN_PROGRESS
    - Không cho update khi COMPLETED hoặc CANCELLED
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Kiểm tra role
        if user.role.role_name != 'STAFF':
            return jsonify({'error': 'Chỉ nhân viên mới có quyền cập nhật tiến độ'}), 403
        
        # Kiểm tra đơn tồn tại
        order = Order.query.get_or_404(order_id)
        
        # Kiểm tra staff có được phân công không
        is_assigned, assignment = check_staff_assignment(order_id, user_id)
        if not is_assigned:
            return jsonify({'error': 'Bạn không được phân công cho đơn hàng này'}), 403
        
        # Kiểm tra trạng thái đơn
        if order.status.status_code not in ['IN_PROGRESS']:
            return jsonify({
                'error': f'Không thể cập nhật tiến độ. Đơn hàng đang ở trạng thái: {order.status.status_name}'
            }), 400
        
        # Lấy dữ liệu
        data = request.get_json()
        progress_note = data.get('progress_note')
        
        if not progress_note or not progress_note.strip():
            return jsonify({'error': 'Ghi chú tiến độ là bắt buộc'}), 400
        
        # Tạo bản ghi tiến độ
        progress = OrderProgress(
            order_id=order_id,
            staff_id=user_id,
            progress_note=progress_note.strip(),
            issue_report=data.get('issue_report')
        )
        
        # Xử lý image_urls
        if data.get('image_urls'):
            progress.set_image_urls(data.get('image_urls'))
        
        db.session.add(progress)
        db.session.commit()
        
        return jsonify({
            'message': 'Đã cập nhật tiến độ thành công',
            'progress': progress.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== 5. HOÀN THÀNH CÔNG VIỆC ====================
@staff_bp.route('/orders/<int:order_id>/complete', methods=['PUT'])
@jwt_required()
def complete_order(order_id):
    """
    Staff hoàn thành công việc - chuyển trạng thái từ IN_PROGRESS → COMPLETED
    Điều kiện:
    - Staff được phân công
    - Trạng thái hiện tại = IN_PROGRESS
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Kiểm tra role
        if user.role.role_name != 'STAFF':
            return jsonify({'error': 'Chỉ nhân viên mới có quyền thao tác'}), 403
        
        # Kiểm tra đơn tồn tại
        order = Order.query.get_or_404(order_id)
        
        # Kiểm tra staff có được phân công không
        is_assigned, assignment = check_staff_assignment(order_id, user_id)
        if not is_assigned:
            return jsonify({'error': 'Bạn không được phân công cho đơn hàng này'}), 403
        
        # Kiểm tra trạng thái hiện tại
        if order.status.status_code != 'IN_PROGRESS':
            return jsonify({
                'error': f'Không thể hoàn thành. Đơn hàng đang ở trạng thái: {order.status.status_name}'
            }), 400
        
        # Lấy trạng thái COMPLETED
        completed_status = OrderStatus.query.filter_by(status_code='COMPLETED').first()
        if not completed_status:
            return jsonify({'error': 'Lỗi hệ thống: Trạng thái COMPLETED chưa được cấu hình'}), 500
        
        # ATOMIC: Cập nhật trạng thái + Ghi lịch sử
        old_status_id = order.status_id
        
        # Ghi lịch sử
        history = OrderStatusHistory(
            order_id=order_id,
            old_status_id=old_status_id,
            new_status_id=completed_status.status_id,
            changed_by=user_id,
            change_reason='Nhân viên hoàn thành công việc'
        )
        db.session.add(history)
        
        # Cập nhật trạng thái
        order.status_id = completed_status.status_id
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Đã hoàn thành công việc thành công',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== 6. LẤY LỊCH SỬ TIẾN ĐỘ ====================
@staff_bp.route('/orders/<int:order_id>/progress', methods=['GET'])
@jwt_required()
def get_order_progress(order_id):
    """
    Lấy lịch sử tiến độ của đơn hàng
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Kiểm tra role
        if user.role.role_name != 'STAFF':
            return jsonify({'error': 'Chỉ nhân viên mới có quyền truy cập'}), 403
        
        # Kiểm tra đơn tồn tại
        order = Order.query.get_or_404(order_id)
        
        # Kiểm tra staff có được phân công không
        is_assigned, assignment = check_staff_assignment(order_id, user_id)
        if not is_assigned:
            return jsonify({'error': 'Bạn không có quyền xem đơn hàng này'}), 403
        
        # Lấy lịch sử tiến độ
        progress_records = OrderProgress.query.filter_by(order_id=order_id)\
            .order_by(OrderProgress.created_at.desc()).all()
        
        return jsonify([p.to_dict() for p in progress_records]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
