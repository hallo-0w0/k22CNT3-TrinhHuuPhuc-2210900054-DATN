"""
Invoices Routes - CRUD
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.invoice import Invoice
from models.order import Order
from models.user import User
from utils.decorators import roles_required
from utils.helpers import create_activity_log, paginate_query
from datetime import datetime

invoices_bp = Blueprint('invoices', __name__)

@invoices_bp.route('', methods=['GET'])
@jwt_required()
def get_invoices():
    """Lấy danh sách invoices"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        customer_id = request.args.get('customer_id', type=int)
        
        query = Invoice.query
        
        # CUSTOMER chỉ xem invoice của mình
        if current_user.is_customer():
            query = query.filter_by(customer_id=current_user_id)
        # ADMIN có thể filter theo customer_id
        
        if customer_id and current_user.is_admin():
            query = query.filter_by(customer_id=customer_id)
        
        result = paginate_query(query.order_by(Invoice.invoice_date.desc()), page, per_page)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy danh sách invoices',
            'error': str(e)
        }), 500

@invoices_bp.route('/<int:invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Lấy chi tiết invoice"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        invoice = Invoice.query.get_or_404(invoice_id)
        
        # Kiểm tra quyền
        if current_user.is_customer() and invoice.customer_id != current_user_id:
            return jsonify({
                'message': 'Không có quyền xem invoice này',
                'error': 'insufficient_permissions'
            }), 403
        
        return jsonify({
            'invoice': invoice.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Lỗi lấy thông tin invoice',
            'error': str(e)
        }), 500

@invoices_bp.route('', methods=['POST'])
@jwt_required()
@roles_required('ADMIN')
def create_invoice():
    """Tạo invoice (ADMIN only, thường tự động khi order COMPLETED)"""
    try:
        data = request.get_json()
        
        if not data.get('order_id'):
            return jsonify({
                'message': 'Thiếu order_id',
                'error': 'missing_field'
            }), 400
        
        order = Order.query.get(data['order_id'])
        if not order:
            return jsonify({
                'message': 'Đơn hàng không tồn tại',
                'error': 'order_not_found'
            }), 404
        
        # Check invoice already exists
        if Invoice.query.filter_by(order_id=order.order_id).first():
            return jsonify({
                'message': 'Invoice đã tồn tại cho đơn này',
                'error': 'invoice_exists'
            }), 400
        
        invoice = Invoice(
            invoice_code=Invoice.generate_invoice_code(),
            order_id=order.order_id,
            customer_id=order.customer_id,
            subtotal=float(order.total_amount) + float(order.discount_amount),
            discount_amount=order.discount_amount,
            tax_amount=data.get('tax_amount', 0),
            total_amount=order.total_amount + (data.get('tax_amount', 0) or 0),
            payment_status=data.get('payment_status', 'PENDING'),
            payment_method=data.get('payment_method'),
            notes=data.get('notes')
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        # Activity log
        current_user_id = get_jwt_identity()
        create_activity_log(current_user_id, 'CREATE', 'Invoice', invoice.invoice_id, f'Tạo invoice: {invoice.invoice_code}')
        
        return jsonify({
            'message': 'Tạo invoice thành công',
            'invoice': invoice.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi tạo invoice',
            'error': str(e)
        }), 500

@invoices_bp.route('/<int:invoice_id>', methods=['PUT'])
@jwt_required()
@roles_required('ADMIN')
def update_invoice(invoice_id):
    """Cập nhật invoice (ADMIN only)"""
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        data = request.get_json()
        
        if 'payment_status' in data:
            invoice.payment_status = data['payment_status']
        if 'payment_date' in data:
            from datetime import datetime
            invoice.payment_date = datetime.fromisoformat(data['payment_date'].replace('Z', '+00:00'))
        if 'payment_method' in data:
            invoice.payment_method = data.get('payment_method')
        if 'notes' in data:
            invoice.notes = data.get('notes')
        
        db.session.commit()
        
        # Activity log
        current_user_id = get_jwt_identity()
        create_activity_log(current_user_id, 'UPDATE', 'Invoice', invoice.invoice_id, f'Cập nhật invoice: {invoice.invoice_code}')
        
        return jsonify({
            'message': 'Cập nhật invoice thành công',
            'invoice': invoice.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi cập nhật invoice',
            'error': str(e)
        }), 500
