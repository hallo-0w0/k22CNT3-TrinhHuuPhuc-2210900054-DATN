"""
Model: ActivityLog
"""
from app import db
from datetime import datetime

class ActivityLog(db.Model):
    __tablename__ = 'ActivityLogs'
    
    log_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=True)
    action_type = db.Column(db.NVARCHAR(100), nullable=False)
    entity_type = db.Column(db.NVARCHAR(100))
    entity_id = db.Column(db.Integer)
    description = db.Column(db.NVARCHAR(1000))
    ip_address = db.Column(db.NVARCHAR(50))
    user_agent = db.Column(db.NVARCHAR(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'action_type': self.action_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ActivityLog {self.action_type} {self.entity_type}:{self.entity_id}>'
