"""
Model: OrderStatusHistory
"""
from app import db
from datetime import datetime

class OrderStatusHistory(db.Model):
    __tablename__ = 'OrderStatusHistory'
    
    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id', ondelete='CASCADE'), nullable=False)
    old_status_id = db.Column(db.Integer, db.ForeignKey('OrderStatus.status_id'), nullable=True)
    new_status_id = db.Column(db.Integer, db.ForeignKey('OrderStatus.status_id'), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    change_reason = db.Column(db.NVARCHAR(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    # changer được định nghĩa trong User model
    
    def to_dict(self):
        return {
            'history_id': self.history_id,
            'order_id': self.order_id,
            'order_code': self.order.order_code if self.order else None,
            'old_status_id': self.old_status_id,
            'old_status_name': self.old_status.status_name if self.old_status else None,
            'new_status_id': self.new_status_id,
            'new_status_name': self.new_status.status_name if self.new_status else None,
            'changed_by': self.changed_by,
            'changer_name': self.changer.full_name if self.changer else None,
            'change_reason': self.change_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<OrderStatusHistory Order:{self.order_id} Status:{self.old_status_id}->{self.new_status_id}>'
