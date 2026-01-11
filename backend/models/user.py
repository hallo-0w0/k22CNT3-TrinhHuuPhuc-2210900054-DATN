"""
Model: User
"""
from app import db
from datetime import datetime
import bcrypt

class User(db.Model):
    __tablename__ = 'Users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.NVARCHAR(100), nullable=False, unique=True)
    email = db.Column(db.NVARCHAR(255), nullable=False, unique=True)
    password_hash = db.Column(db.NVARCHAR(255), nullable=False)
    full_name = db.Column(db.NVARCHAR(255), nullable=False)
    phone_number = db.Column(db.NVARCHAR(20))
    address = db.Column(db.NVARCHAR(500))
    role_id = db.Column(db.Integer, db.ForeignKey('Roles.role_id'), nullable=False)
    member_level_id = db.Column(db.Integer, db.ForeignKey('MemberLevels.member_level_id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_locked = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', foreign_keys='Order.customer_id', backref='customer', lazy=True)
    assigned_orders = db.relationship('OrderAssignment', foreign_keys='OrderAssignment.staff_id', backref='staff', lazy=True)
    reviews = db.relationship('Review', foreign_keys='Review.customer_id', backref='reviewer', lazy=True)
    review_responses = db.relationship('Review', foreign_keys='Review.admin_response_by', backref='admin_responder', lazy=True)
    consultations_handled = db.relationship('Consultation', foreign_keys='Consultation.handled_by', backref='handler', lazy=True)
    contents_created = db.relationship('Content', foreign_keys='Content.created_by', backref='creator', lazy=True)
    contents_updated = db.relationship('Content', foreign_keys='Content.updated_by', backref='updater', lazy=True)
    config_updates = db.relationship('SystemConfig', foreign_keys='SystemConfig.updated_by', backref='updater', lazy=True)
    status_changes = db.relationship('OrderStatusHistory', foreign_keys='OrderStatusHistory.changed_by', backref='changer', lazy=True)
    progress_reports = db.relationship('OrderProgress', foreign_keys='OrderProgress.staff_id', backref='staff', lazy=True)
    assignments_made = db.relationship('OrderAssignment', foreign_keys='OrderAssignment.assigned_by', backref='assigner', lazy=True)
    invoices = db.relationship('Invoice', foreign_keys='Invoice.customer_id', backref='customer', lazy=True)
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash và lưu password"""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def check_password(self, password):
        """Kiểm tra password"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def to_dict(self, include_sensitive=False):
        """Chuyển đổi sang dictionary"""
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'address': self.address,
            'role_id': self.role_id,
            'role_name': self.role.role_name if self.role else None,
            'member_level_id': self.member_level_id,
            'member_level_code': self.member_level.level_code if self.member_level else None,
            'member_level_name': self.member_level.level_name if self.member_level else None,
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    def is_customer(self):
        """Kiểm tra có phải CUSTOMER không"""
        return self.role and self.role.role_name == 'CUSTOMER'
    
    def is_staff(self):
        """Kiểm tra có phải STAFF không"""
        return self.role and self.role.role_name == 'STAFF'
    
    def is_admin(self):
        """Kiểm tra có phải ADMIN không"""
        return self.role and self.role.role_name == 'ADMIN'
    
    def __repr__(self):
        return f'<User {self.username}>'
