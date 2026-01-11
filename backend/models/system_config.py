"""
Model: SystemConfig
"""
from app import db
from datetime import datetime

class SystemConfig(db.Model):
    __tablename__ = 'SystemConfig'
    
    config_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_key = db.Column(db.NVARCHAR(100), nullable=False, unique=True)
    config_value = db.Column(db.UnicodeText)  # NVARCHAR(MAX) equivalent
    config_type = db.Column(db.NVARCHAR(50))
    description = db.Column(db.NVARCHAR(500))
    updated_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # updater được định nghĩa trong User model
    
    def to_dict(self):
        return {
            'config_id': self.config_id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'config_type': self.config_type,
            'description': self.description,
            'updated_by': self.updated_by,
            'updated_by_name': self.updater.full_name if self.updater else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<SystemConfig {self.config_key}>'
