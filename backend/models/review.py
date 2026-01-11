"""
Model: Review
"""
from app import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'Reviews'
    
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    review_text = db.Column(db.NVARCHAR(1000))
    is_public = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    admin_response = db.Column(db.NVARCHAR(500))
    admin_response_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=True)
    admin_response_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # admin_responder được định nghĩa trong User model
    
    def to_dict(self):
        return {
            'review_id': self.review_id,
            'order_id': self.order_id,
            'order_code': self.order.order_code if self.order else None,
            'customer_id': self.customer_id,
            'customer_name': self.reviewer.full_name if self.reviewer else None,
            'rating': self.rating,
            'review_text': self.review_text,
            'is_public': self.is_public,
            'is_verified': self.is_verified,
            'admin_response': self.admin_response,
            'admin_response_by': self.admin_response_by,
            'admin_response_by_name': self.admin_responder.full_name if self.admin_responder else None,
            'admin_response_at': self.admin_response_at.isoformat() if self.admin_response_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Review Order:{self.order_id} Rating:{self.rating}>'
