from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import db
from backend.models.user import User, Role
from backend.models.service import Service, ServiceCategory
from backend.models.order import Order, OrderStatus, OrderProgress, OrderAssignment
from backend.models.content import Content
from datetime import datetime
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def require_admin():
    """Helper function để kiểm tra user là ADMIN"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return None
        user = User.query.get(user_id)
        if not user:
            return None
        if user.role.role_name != 'ADMIN':
            return None
        return user
    except Exception as e:
        print(f"Error in require_admin: {e}")
        return None

# ==================== DASHBOARD ====================
@admin_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Lấy thống kê tổng quan cho dashboard"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Không có quyền truy cập. Yêu cầu quyền ADMIN.'}), 403
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Lỗi xác thực: {str(e)}'}), 403
    
    try:
        # Tổng số người dùng
        total_users = User.query.count()
        
        # Tổng số đơn dịch vụ
        total_orders = Order.query.count()
        
        # Tổng doanh thu (từ các đơn COMPLETED)
        completed_status = OrderStatus.query.filter_by(status_code='COMPLETED').first()
        total_revenue = 0
        if completed_status:
            result = db.session.query(func.sum(Order.total_amount)).filter_by(
                status_id=completed_status.status_id
            ).scalar()
            total_revenue = float(result) if result else 0
        
        # Đơn chờ xử lý
        pending_status = OrderStatus.query.filter_by(status_code='PENDING').first()
        pending_orders = 0
        if pending_status:
            pending_orders = Order.query.filter_by(status_id=pending_status.status_id).count()
        
        # Đơn hoàn thành
        completed_orders = 0
        if completed_status:
            completed_orders = Order.query.filter_by(status_id=completed_status.status_id).count()
        
        return jsonify({
            'total_users': total_users,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== SERVICES ====================
@admin_bp.route('/services', methods=['GET'])
@jwt_required()
def admin_get_services():
    """Lấy danh sách dịch vụ (admin)"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Không có quyền truy cập. Yêu cầu quyền ADMIN.'}), 403
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Lỗi xác thực: {str(e)}'}), 403
    
    try:
        services = Service.query.order_by(Service.display_order, Service.service_name).all()
        result = [s.to_dict() for s in services]
        return jsonify(result), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services', methods=['POST'])
@jwt_required()
def admin_create_service():
    """Tạo dịch vụ mới"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        data = request.get_json()
        
        service_name = (data.get('service_name') or '').strip()
        service_description = (data.get('service_description') or '').strip()
        category_id = data.get('category_id')
        base_price = data.get('base_price')
        duration_hours = data.get('duration_hours')
        unit = (data.get('unit') or '').strip()
        is_active = data.get('is_active', True)
        display_order = data.get('display_order', 0)
        
        if not service_name or not category_id or base_price is None:
            return jsonify({'error': 'service_name, category_id, base_price là bắt buộc'}), 400
        
        # Kiểm tra category tồn tại
        category = ServiceCategory.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category không tồn tại'}), 400
        
        service = Service(
            service_name=service_name,
            service_description=service_description,
            category_id=category_id,
            base_price=base_price,
            duration_hours=duration_hours,
            unit=unit,
            is_active=is_active,
            display_order=display_order
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify(service.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services/<int:service_id>', methods=['GET'])
@jwt_required()
def admin_get_service(service_id):
    """Lấy chi tiết dịch vụ"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        service = Service.query.get_or_404(service_id)
        return jsonify(service.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services/<int:service_id>', methods=['PUT'])
@jwt_required()
def admin_update_service(service_id):
    """Cập nhật dịch vụ"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        service = Service.query.get_or_404(service_id)
        data = request.get_json()
        
        if 'service_name' in data:
            service.service_name = (data['service_name'] or '').strip()
        if 'service_description' in data:
            service.service_description = (data.get('service_description') or '').strip()
        if 'category_id' in data:
            category = ServiceCategory.query.get(data['category_id'])
            if not category:
                return jsonify({'error': 'Category không tồn tại'}), 400
            service.category_id = data['category_id']
        if 'base_price' in data:
            service.base_price = data['base_price']
        if 'duration_hours' in data:
            service.duration_hours = data.get('duration_hours')
        if 'unit' in data:
            service.unit = (data.get('unit') or '').strip()
        if 'is_active' in data:
            service.is_active = data['is_active']
        if 'display_order' in data:
            service.display_order = data.get('display_order', 0)
        
        service.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(service.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services/<int:service_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_service(service_id):
    """Xóa dịch vụ"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        service = Service.query.get_or_404(service_id)
        
        # Kiểm tra xem có đơn hàng nào đang sử dụng dịch vụ này không
        orders_count = Order.query.filter_by(service_id=service_id).count()
        if orders_count > 0:
            return jsonify({'error': f'Không thể xóa dịch vụ. Có {orders_count} đơn hàng đang sử dụng dịch vụ này.'}), 400
        
        db.session.delete(service)
        db.session.commit()
        
        return jsonify({'message': 'Xóa dịch vụ thành công'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== CATEGORIES ====================
@admin_bp.route('/categories', methods=['GET'])
@jwt_required()
def admin_get_categories():
    """Lấy danh sách categories"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Không có quyền truy cập. Yêu cầu quyền ADMIN.'}), 403
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Lỗi xác thực: {str(e)}'}), 403
    
    try:
        categories = ServiceCategory.query.order_by(
            ServiceCategory.display_order, ServiceCategory.category_name
        ).all()
        result = [c.to_dict() for c in categories]
        return jsonify(result), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/categories', methods=['POST'])
@jwt_required()
def admin_create_category():
    """Tạo category mới"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        data = request.get_json()
        
        category_name = (data.get('category_name') or '').strip()
        category_description = (data.get('category_description') or '').strip()
        display_order = data.get('display_order', 0)
        is_active = data.get('is_active', True)
        
        if not category_name:
            return jsonify({'error': 'category_name là bắt buộc'}), 400
        
        category = ServiceCategory(
            category_name=category_name,
            category_description=category_description,
            display_order=display_order,
            is_active=is_active
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify(category.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def admin_update_category(category_id):
    """Cập nhật category"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        category = ServiceCategory.query.get_or_404(category_id)
        data = request.get_json()
        
        if 'category_name' in data:
            category.category_name = (data['category_name'] or '').strip()
        if 'category_description' in data:
            category.category_description = (data.get('category_description') or '').strip()
        if 'display_order' in data:
            category.display_order = data.get('display_order', 0)
        if 'is_active' in data:
            category.is_active = data['is_active']
        
        category.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(category.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_category(category_id):
    """Xóa category"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        category = ServiceCategory.query.get_or_404(category_id)
        
        # Kiểm tra xem có dịch vụ nào đang sử dụng category này không
        services_count = Service.query.filter_by(category_id=category_id).count()
        if services_count > 0:
            return jsonify({
                'error': f'Không thể xóa category. Có {services_count} dịch vụ đang sử dụng category này.'
            }), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'message': 'Xóa category thành công'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== USERS ====================
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def admin_get_users():
    """Lấy danh sách users"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Không có quyền truy cập. Yêu cầu quyền ADMIN.'}), 403
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Lỗi xác thực: {str(e)}'}), 403
    
    try:
        role_filter = request.args.get('role')
        query = User.query
        
        if role_filter:
            role = Role.query.filter_by(role_name=role_filter.upper()).first()
            if role:
                query = query.filter_by(role_id=role.role_id)
        
        users = query.order_by(User.created_at.desc()).all()
        result = [u.to_dict(include_sensitive=True) for u in users]
        return jsonify(result), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def admin_get_user(user_id):
    """Lấy chi tiết user"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict(include_sensitive=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
def admin_update_user_status(user_id):
    """Cập nhật trạng thái user (lock/unlock)"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'is_locked' in data:
            user.is_locked = bool(data['is_locked'])
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(user.to_dict(include_sensitive=True)), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== ORDERS ====================
@admin_bp.route('/orders/<int:order_id>/assign', methods=['POST'])
@jwt_required()
def admin_assign_order(order_id):
    """Gán staff cho đơn hàng"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        staff_id = data.get('staff_id')
        notes = data.get('notes')
        
        if not staff_id:
            return jsonify({'error': 'staff_id là bắt buộc'}), 400
            
        try:
            staff_id = int(staff_id)
        except ValueError:
            return jsonify({'error': 'staff_id phải là số'}), 400
            
        status_code = order.status.status_code
        
        # Validate status logic
        if status_code in ['PENDING', 'COMPLETED', 'CANCELLED']:
            return jsonify({'error': f'Không thể phân công nhân viên ở trạng thái {status_code}'}), 400
            
        # Kiểm tra staff tồn tại và là STAFF
        staff = User.query.get(staff_id)
        if not staff or staff.role.role_name != 'STAFF':
            return jsonify({'error': 'Staff không tồn tại hoặc không phải STAFF'}), 400
            
        # Logic phân công theo trạng thái
        if status_code == 'CONFIRMED':
            # Giai đoạn 2: Chỉ 1 nhân viên chính -> Gỡ người cũ (nếu có)
            # Trước khi set False, kiểm tra xem việc set False có gây trùng lặp không (UQ_Order_Staff_Active)
            current_assignments = OrderAssignment.query.filter_by(order_id=order_id, is_active=True).all()
            for ca in current_assignments:
                # Kiểm tra xem đã có bản ghi inactive của staff này chưa
                existing_inactive = OrderAssignment.query.filter_by(
                    order_id=order_id, 
                    staff_id=ca.staff_id, 
                    is_active=False
                ).first()
                if existing_inactive:
                    # Nếu đã có, xóa cái cũ đi để nhường chỗ cho cái mới (giữ lại history mới nhất)
                    db.session.delete(existing_inactive)
            
            # Sau khi dọn dẹp, mới update active=False
            OrderAssignment.query.filter_by(order_id=order_id, is_active=True).update({'is_active': False})
            
            if not notes:
                notes = "Nhân viên chính"
                
        elif status_code == 'IN_PROGRESS':
            # Giai đoạn 3: Cho phép thêm người hỗ trợ -> KHÔNG gỡ người cũ
            # Kiểm tra xem staff này đã được assign chưa
            existing = OrderAssignment.query.filter_by(
                order_id=order_id, 
                staff_id=staff_id, 
                is_active=True
            ).first()
            if existing:
                return jsonify({'error': f'Nhân viên {staff.full_name} đã được phân công vào đơn hàng này rồi'}), 400
                
            if not notes:
                notes = "Nhân viên hỗ trợ"
        
        # Tạo assignment mới
        assignment = OrderAssignment(
            order_id=order_id,
            staff_id=staff_id,
            assigned_by=admin.user_id,
            notes=notes
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        return jsonify(assignment.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== STAFF ====================
@admin_bp.route('/staff', methods=['GET'])
@jwt_required()
def admin_get_staff():
    """Lấy danh sách staff"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Không có quyền truy cập. Yêu cầu quyền ADMIN.'}), 403
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Lỗi xác thực: {str(e)}'}), 403
    
    try:
        staff_role = Role.query.filter_by(role_name='STAFF').first()
        if not staff_role:
            return jsonify([]), 200
        
        staff = User.query.filter_by(role_id=staff_role.role_id).order_by(User.full_name).all()
        result = [s.to_dict(include_sensitive=True) for s in staff]
        return jsonify(result), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ==================== CONTENT ====================
@admin_bp.route('/content', methods=['GET'])
@jwt_required()
def admin_get_content():
    """Lấy danh sách content (admin)"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Không có quyền truy cập. Yêu cầu quyền ADMIN.'}), 403
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Lỗi xác thực: {str(e)}'}), 403
    
    try:
        content_type = request.args.get('content_type')
        query = Content.query
        
        if content_type:
            query = query.filter_by(content_type=content_type.upper())
        
        contents = query.order_by(Content.display_order, Content.created_at.desc()).all()
        result = [c.to_dict() for c in contents]
        return jsonify(result), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/content', methods=['POST'])
@jwt_required()
def admin_create_content():
    """Tạo content mới"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        data = request.get_json()
        
        content_type = (data.get('content_type') or '').strip().upper()
        title = (data.get('title') or '').strip()
        content_text = data.get('content_text')
        image_url = (data.get('image_url') or '').strip()
        display_order = data.get('display_order', 0)
        is_active = data.get('is_active', True)
        
        if not content_type or not title:
            return jsonify({'error': 'content_type và title là bắt buộc'}), 400
        
        content = Content(
            content_type=content_type,
            title=title,
            content_text=content_text,
            image_url=image_url,
            display_order=display_order,
            is_active=is_active,
            created_by=admin.user_id
        )
        
        db.session.add(content)
        db.session.commit()
        
        return jsonify(content.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/content/<int:content_id>', methods=['PUT'])
@jwt_required()
def admin_update_content(content_id):
    """Cập nhật content"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        content = Content.query.get_or_404(content_id)
        data = request.get_json()
        
        if 'content_type' in data:
            content.content_type = (data['content_type'] or '').strip().upper()
        if 'title' in data:
            content.title = (data['title'] or '').strip()
        if 'content_text' in data:
            content.content_text = data.get('content_text')
        if 'image_url' in data:
            content.image_url = (data.get('image_url') or '').strip()
        if 'display_order' in data:
            content.display_order = data.get('display_order', 0)
        if 'is_active' in data:
            content.is_active = data['is_active']
        
        content.updated_by = admin.user_id
        content.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(content.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/content/<int:content_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_content(content_id):
    """Xóa content"""
    admin = require_admin()
    if not admin:
        return jsonify({'error': 'Không có quyền truy cập'}), 403
    
    try:
        content = Content.query.get_or_404(content_id)
        db.session.delete(content)
        db.session.commit()
        
        return jsonify({'message': 'Xóa content thành công'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
