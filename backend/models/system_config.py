from backend import db
from datetime import datetime

class SystemConfig(db.Model):
    """Bảng SystemConfig"""
    __tablename__ = 'SystemConfig'
    
    config_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_key = db.Column(db.NVARCHAR(100), unique=True, nullable=False)
    config_value = db.Column(db.Text)
    config_type = db.Column(db.NVARCHAR(50))  # STRING, NUMBER, BOOLEAN, JSON
    description = db.Column(db.NVARCHAR(500))
    updated_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    updater = db.relationship('User', backref='updated_configs')
    
    def to_dict(self):
        return {
            'config_id': self.config_id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'config_type': self.config_type,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
