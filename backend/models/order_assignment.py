"""
Model: OrderAssignment
"""
from app import db
from datetime import datetime

class OrderAssignment(db.Model):
    __tablename__ = 'OrderAssignments'
    
    assignment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id', ondelete='CASCADE'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.NVARCHAR(500))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    # assigner được định nghĩa trong User model
    
    def to_dict(self):
        return {
            'assignment_id': self.assignment_id,
            'order_id': self.order_id,
            'order_code': self.order.order_code if self.order else None,
            'staff_id': self.staff_id,
            'staff_name': self.staff.full_name if self.staff else None,
            'assigned_by': self.assigned_by,
            'assigner_name': self.assigner.full_name if self.assigner else None,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'notes': self.notes,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<OrderAssignment Order:{self.order_id} Staff:{self.staff_id}>'
