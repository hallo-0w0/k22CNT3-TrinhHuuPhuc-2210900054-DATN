from backend import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Role(db.Model):
    """Bảng Roles"""
    __tablename__ = 'Roles'
    
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.NVARCHAR(50), unique=True, nullable=False)
    role_description = db.Column(db.NVARCHAR(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='role', lazy=True)
    
    def to_dict(self):
        return {
            'role_id': self.role_id,
            'role_name': self.role_name,
            'role_description': self.role_description
        }

class MemberLevel(db.Model):
    """Bảng MemberLevels"""
    __tablename__ = 'MemberLevels'
    
    member_level_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level_code = db.Column(db.NVARCHAR(20), unique=True, nullable=False)
    level_name = db.Column(db.NVARCHAR(50), nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    min_total_amount = db.Column(db.Numeric(18, 2))
    min_service_count = db.Column(db.Integer)
    min_continuous_months = db.Column(db.Integer)
    description = db.Column(db.NVARCHAR(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='member_level', lazy=True)
    
    def to_dict(self):
        return {
            'member_level_id': self.member_level_id,
            'level_code': self.level_code,
            'level_name': self.level_name,
            'discount_percentage': float(self.discount_percentage),
            'min_total_amount': float(self.min_total_amount) if self.min_total_amount else None,
            'min_service_count': self.min_service_count,
            'min_continuous_months': self.min_continuous_months,
            'description': self.description
        }

class User(db.Model):
    """Bảng Users"""
    __tablename__ = 'Users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.NVARCHAR(100), unique=True, nullable=False)
    email = db.Column(db.NVARCHAR(255), unique=True, nullable=False)
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
    
    def set_password(self, password):
        """Hash password và lưu"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Kiểm tra password"""
        return check_password_hash(self.password_hash, password)
    
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
            'member_level': self.member_level.to_dict() if self.member_level else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_sensitive:
            data['is_locked'] = self.is_locked
            data['last_login'] = self.last_login.isoformat() if self.last_login else None
        return data
