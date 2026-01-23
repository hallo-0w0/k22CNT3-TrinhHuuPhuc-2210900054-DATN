from backend import db
from datetime import datetime

class Review(db.Model):
    """Bảng Reviews"""
    __tablename__ = 'Reviews'
    
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    review_text = db.Column(db.NVARCHAR(1000))
    is_public = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    admin_response = db.Column(db.NVARCHAR(500))
    admin_response_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    admin_response_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref='review', uselist=False)
    customer = db.relationship('User', foreign_keys=[customer_id], backref='reviews')
    admin_responder = db.relationship('User', foreign_keys=[admin_response_by])
    
    def to_dict(self):
        return {
            'review_id': self.review_id,
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'customer': self.customer.to_dict() if self.customer else None,
            'rating': self.rating,
            'review_text': self.review_text,
            'is_public': self.is_public,
            'is_verified': self.is_verified,
            'admin_response': self.admin_response,
            'admin_response_by': self.admin_response_by,
            'admin_response_at': self.admin_response_at.isoformat() if self.admin_response_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
