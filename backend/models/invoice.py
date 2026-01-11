"""
Model: Invoice
"""
from app import db
from datetime import datetime
from decimal import Decimal
import uuid

class Invoice(db.Model):
    __tablename__ = 'Invoices'
    
    invoice_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_code = db.Column(db.NVARCHAR(50), nullable=False, unique=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    subtotal = db.Column(db.Numeric(18, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(18, 2), default=0)
    tax_amount = db.Column(db.Numeric(18, 2), default=0)
    total_amount = db.Column(db.Numeric(18, 2), nullable=False)
    payment_status = db.Column(db.NVARCHAR(50), default='PENDING')
    payment_date = db.Column(db.DateTime)
    payment_method = db.Column(db.NVARCHAR(50))
    notes = db.Column(db.NVARCHAR(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # customer được định nghĩa trong User model
    
    @staticmethod
    def generate_invoice_code():
        """Tạo mã hóa đơn tự động"""
        return f'INV{datetime.utcnow().strftime("%Y%m%d")}{str(uuid.uuid4())[:8].upper()}'
    
    def to_dict(self):
        return {
            'invoice_id': self.invoice_id,
            'invoice_code': self.invoice_code,
            'order_id': self.order_id,
            'order_code': self.order.order_code if self.order else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else None,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'payment_status': self.payment_status,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Invoice {self.invoice_code}>'
