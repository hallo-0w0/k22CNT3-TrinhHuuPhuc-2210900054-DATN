"""
Model: OrderStatus
"""
from app import db

class OrderStatus(db.Model):
    __tablename__ = 'OrderStatus'
    
    status_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_code = db.Column(db.NVARCHAR(50), nullable=False, unique=True)
    status_name = db.Column(db.NVARCHAR(100), nullable=False)
    status_description = db.Column(db.NVARCHAR(255))
    display_order = db.Column(db.Integer, default=0)
    
    # Relationships
    orders = db.relationship('Order', backref='status', lazy=True)
    old_status_history = db.relationship('OrderStatusHistory', foreign_keys='OrderStatusHistory.old_status_id', backref='old_status', lazy=True)
    new_status_history = db.relationship('OrderStatusHistory', foreign_keys='OrderStatusHistory.new_status_id', backref='new_status', lazy=True)
    
    def to_dict(self):
        return {
            'status_id': self.status_id,
            'status_code': self.status_code,
            'status_name': self.status_name,
            'status_description': self.status_description,
            'display_order': self.display_order
        }
    
    def __repr__(self):
        return f'<OrderStatus {self.status_code}>'
