"""
Model: Consultation
"""
from app import db
from datetime import datetime

class Consultation(db.Model):
    __tablename__ = 'Consultations'
    
    consultation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.NVARCHAR(255), nullable=False)
    email = db.Column(db.NVARCHAR(255), nullable=False)
    phone_number = db.Column(db.NVARCHAR(20))
    company_name = db.Column(db.NVARCHAR(255))
    address = db.Column(db.NVARCHAR(500))
    service_interest = db.Column(db.NVARCHAR(500))
    message = db.Column(db.NVARCHAR(1000), nullable=False)
    status = db.Column(db.NVARCHAR(50), default='PENDING')
    handled_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=True)
    response_message = db.Column(db.NVARCHAR(1000))
    handled_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # handler được định nghĩa trong User model
    
    def to_dict(self):
        return {
            'consultation_id': self.consultation_id,
            'full_name': self.full_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'company_name': self.company_name,
            'address': self.address,
            'service_interest': self.service_interest,
            'message': self.message,
            'status': self.status,
            'handled_by': self.handled_by,
            'handler_name': self.handler.full_name if self.handler else None,
            'response_message': self.response_message,
            'handled_at': self.handled_at.isoformat() if self.handled_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Consultation {self.full_name}>'
