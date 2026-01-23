from backend import db
from datetime import datetime

class ServiceCategory(db.Model):
    """Bảng ServiceCategories"""
    __tablename__ = 'ServiceCategories'
    
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.NVARCHAR(255), nullable=False)
    category_description = db.Column(db.NVARCHAR(500))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    services = db.relationship('Service', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'category_id': self.category_id,
            'category_name': self.category_name,
            'category_description': self.category_description,
            'display_order': self.display_order,
            'is_active': self.is_active
        }

class Service(db.Model):
    """Bảng Services"""
    __tablename__ = 'Services'
    
    service_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_name = db.Column(db.NVARCHAR(255), nullable=False)
    service_description = db.Column(db.NVARCHAR(1000))
    category_id = db.Column(db.Integer, db.ForeignKey('ServiceCategories.category_id'), nullable=False)
    base_price = db.Column(db.Numeric(18, 2), nullable=False)
    duration_hours = db.Column(db.Numeric(5, 2))
    unit = db.Column(db.NVARCHAR(50))
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='service', lazy=True)
    
    def to_dict(self):
        return {
            'service_id': self.service_id,
            'service_name': self.service_name,
            'service_description': self.service_description,
            'category_id': self.category_id,
            'category': self.category.to_dict() if self.category else None,
            'base_price': float(self.base_price),
            'duration_hours': float(self.duration_hours) if self.duration_hours else None,
            'unit': self.unit,
            'is_active': self.is_active,
            'display_order': self.display_order
        }
