"""
Model: Order
"""
from app import db
from datetime import datetime
from decimal import Decimal
import uuid

class Order(db.Model):
    __tablename__ = 'Orders'
    
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_code = db.Column(db.NVARCHAR(50), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('Services.service_id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    scheduled_time = db.Column(db.Time)
    service_address = db.Column(db.NVARCHAR(500), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), default=1)
    unit_price = db.Column(db.Numeric(18, 2), nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    discount_amount = db.Column(db.Numeric(18, 2), default=0)
    total_amount = db.Column(db.Numeric(18, 2), nullable=False)
    notes = db.Column(db.NVARCHAR(1000))
    status_id = db.Column(db.Integer, db.ForeignKey('OrderStatus.status_id'), nullable=False, default=1)
    priority = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('OrderAssignment', backref='order', lazy=True)
    status_history = db.relationship('OrderStatusHistory', backref='order', lazy=True, order_by='OrderStatusHistory.created_at')
    progress = db.relationship('OrderProgress', backref='order', lazy=True)
    invoice = db.relationship('Invoice', backref='order', uselist=False, lazy=True)
    review = db.relationship('Review', backref='order', uselist=False, lazy=True)
    
    @staticmethod
    def generate_order_code():
        """Tạo mã đơn hàng tự động"""
        return f'ORD{datetime.utcnow().strftime("%Y%m%d")}{str(uuid.uuid4())[:8].upper()}'
    
    def calculate_total(self):
        """Tính tổng tiền sau giảm giá"""
        subtotal = float(self.unit_price) * float(self.quantity)
        discount = subtotal * (float(self.discount_percentage) / 100)
        self.discount_amount = Decimal(str(discount))
        self.total_amount = Decimal(str(subtotal - discount))
    
    def to_dict(self):
        return {
            'order_id': self.order_id,
            'order_code': self.order_code,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else None,
            'service_id': self.service_id,
            'service_name': self.service.service_name if self.service else None,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'scheduled_time': self.scheduled_time.strftime('%H:%M:%S') if self.scheduled_time else None,
            'service_address': self.service_address,
            'quantity': float(self.quantity) if self.quantity else 1,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'discount_percentage': float(self.discount_percentage) if self.discount_percentage else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'notes': self.notes,
            'status_id': self.status_id,
            'status_code': self.status.status_code if self.status else None,
            'status_name': self.status.status_name if self.status else None,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Order {self.order_code}>'
