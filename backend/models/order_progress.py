"""
Model: OrderProgress
"""
from app import db
from datetime import datetime
import json

class OrderProgress(db.Model):
    __tablename__ = 'OrderProgress'
    
    progress_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id', ondelete='CASCADE'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    progress_note = db.Column(db.NVARCHAR(1000))
    image_urls = db.Column(db.UnicodeText)  # JSON array - NVARCHAR(MAX) equivalent
    issue_report = db.Column(db.NVARCHAR(1000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    # staff được định nghĩa trong User model
    
    def set_image_urls(self, urls):
        """Set image URLs từ list"""
        if urls:
            self.image_urls = json.dumps(urls)
        else:
            self.image_urls = None
    
    def get_image_urls(self):
        """Get image URLs thành list"""
        if self.image_urls:
            try:
                return json.loads(self.image_urls)
            except:
                return []
        return []
    
    def to_dict(self):
        return {
            'progress_id': self.progress_id,
            'order_id': self.order_id,
            'order_code': self.order.order_code if self.order else None,
            'staff_id': self.staff_id,
            'staff_name': self.staff.full_name if self.staff else None,
            'progress_note': self.progress_note,
            'image_urls': self.get_image_urls(),
            'issue_report': self.issue_report,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<OrderProgress Order:{self.order_id} Staff:{self.staff_id}>'
