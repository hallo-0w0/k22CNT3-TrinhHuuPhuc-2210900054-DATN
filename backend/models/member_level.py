"""
Model: MemberLevel
"""
from app import db
from datetime import datetime
from decimal import Decimal

class MemberLevel(db.Model):
    __tablename__ = 'MemberLevels'
    
    member_level_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level_code = db.Column(db.NVARCHAR(20), nullable=False, unique=True)
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
            'discount_percentage': float(self.discount_percentage) if self.discount_percentage else 0,
            'min_total_amount': float(self.min_total_amount) if self.min_total_amount else None,
            'min_service_count': self.min_service_count,
            'min_continuous_months': self.min_continuous_months,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<MemberLevel {self.level_code}>'
