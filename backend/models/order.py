from backend import db
from datetime import datetime
import json

class OrderStatus(db.Model):
    """Bảng OrderStatus"""
    __tablename__ = 'OrderStatus'
    
    status_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_code = db.Column(db.NVARCHAR(50), unique=True, nullable=False)
    status_name = db.Column(db.NVARCHAR(100), nullable=False)
    status_description = db.Column(db.NVARCHAR(255))
    display_order = db.Column(db.Integer, default=0)
    
    # Relationships
    orders = db.relationship('Order', backref='status', lazy=True)
    
    def to_dict(self):
        return {
            'status_id': self.status_id,
            'status_code': self.status_code,
            'status_name': self.status_name,
            'status_description': self.status_description
        }

class Order(db.Model):
    """Bảng Orders"""
    __tablename__ = 'Orders'
    
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_code = db.Column(db.NVARCHAR(50), unique=True, nullable=False)
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
    assignments = db.relationship('OrderAssignment', backref='order', lazy=True, cascade='all, delete-orphan')
    progress_records = db.relationship('OrderProgress', backref='order', lazy=True, cascade='all, delete-orphan')
    status_history = db.relationship('OrderStatusHistory', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'order_id': self.order_id,
            'order_code': self.order_code,
            'customer_id': self.customer_id,
            'customer': self.customer.to_dict() if self.customer else None,
            'service_id': self.service_id,
            'service': self.service.to_dict() if self.service else None,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'scheduled_time': str(self.scheduled_time) if self.scheduled_time else None,
            'service_address': self.service_address,
            'quantity': float(self.quantity),
            'unit_price': float(self.unit_price),
            'discount_percentage': float(self.discount_percentage),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'notes': self.notes,
            'status_id': self.status_id,
            'status': self.status.to_dict() if self.status else None,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'assignments': [a.to_dict() for a in self.assignments] if self.assignments else [],
            'status_history': [h.to_dict() for h in self.status_history] if self.status_history else []
        }

class OrderAssignment(db.Model):
    """Bảng OrderAssignments"""
    __tablename__ = 'OrderAssignments'
    
    assignment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id', ondelete='CASCADE'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.NVARCHAR(500))
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'assignment_id': self.assignment_id,
            'order_id': self.order_id,
            'staff_id': self.staff_id,
            'staff': self.staff.to_dict() if self.staff else None,
            'assigned_by': self.assigned_by,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'notes': self.notes,
            'is_active': self.is_active
        }

class OrderStatusHistory(db.Model):
    """Bảng OrderStatusHistory"""
    __tablename__ = 'OrderStatusHistory'
    
    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id', ondelete='CASCADE'), nullable=False)
    old_status_id = db.Column(db.Integer, db.ForeignKey('OrderStatus.status_id'))
    new_status_id = db.Column(db.Integer, db.ForeignKey('OrderStatus.status_id'), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    change_reason = db.Column(db.NVARCHAR(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'history_id': self.history_id,
            'order_id': self.order_id,
            'old_status_id': self.old_status_id,
            'new_status_id': self.new_status_id,
            'changed_by': self.changed_by,
            'change_reason': self.change_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OrderProgress(db.Model):
    """Bảng OrderProgress"""
    __tablename__ = 'OrderProgress'
    
    progress_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id', ondelete='CASCADE'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    progress_note = db.Column(db.NVARCHAR(1000))
    image_urls = db.Column(db.Text)  # JSON array
    issue_report = db.Column(db.NVARCHAR(1000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    staff = db.relationship('User', foreign_keys=[staff_id], backref='progress_updates', lazy=True)
    
    def get_image_urls(self):
        """Parse image_urls từ JSON string"""
        if self.image_urls:
            try:
                return json.loads(self.image_urls)
            except:
                return []
        return []
    
    def set_image_urls(self, urls):
        """Lưu image_urls dạng JSON string"""
        if isinstance(urls, list):
            self.image_urls = json.dumps(urls)
        else:
            self.image_urls = urls
    
    def to_dict(self):
        return {
            'progress_id': self.progress_id,
            'order_id': self.order_id,
            'staff_id': self.staff_id,
            'staff': self.staff.to_dict() if self.staff else None,
            'progress_note': self.progress_note,
            'image_urls': self.get_image_urls(),
            'issue_report': self.issue_report,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
