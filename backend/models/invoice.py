from backend import db
from datetime import datetime

class Invoice(db.Model):
    """Bảng Invoices"""
    __tablename__ = 'Invoices'
    
    invoice_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_code = db.Column(db.NVARCHAR(50), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'), unique=True, nullable=False)
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
    order = db.relationship('Order', backref='invoice', uselist=False)
    customer = db.relationship('User', foreign_keys=[customer_id], backref='invoices')
    
    def to_dict(self):
        return {
            'invoice_id': self.invoice_id,
            'invoice_code': self.invoice_code,
            'order_id': self.order_id,
            'order': self.order.to_dict() if self.order else None,
            'customer_id': self.customer_id,
            'customer': self.customer.to_dict() if self.customer else None,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'subtotal': float(self.subtotal),
            'discount_amount': float(self.discount_amount),
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount),
            'payment_status': self.payment_status,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'notes': self.notes
        }
