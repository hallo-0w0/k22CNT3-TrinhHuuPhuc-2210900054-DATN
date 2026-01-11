"""
Model: Content
"""
from app import db
from datetime import datetime

class Content(db.Model):
    __tablename__ = 'Content'
    
    content_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content_type = db.Column(db.NVARCHAR(50), nullable=False)
    title = db.Column(db.NVARCHAR(255), nullable=False)
    content_text = db.Column(db.UnicodeText)  # NVARCHAR(MAX) equivalent
    image_url = db.Column(db.NVARCHAR(500))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # creator và updater được định nghĩa trong User model
    
    def to_dict(self):
        return {
            'content_id': self.content_id,
            'content_type': self.content_type,
            'title': self.title,
            'content_text': self.content_text,
            'image_url': self.image_url,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_by_name': self.creator.full_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_by': self.updated_by,
            'updated_by_name': self.updater.full_name if self.updater else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Content {self.content_type}:{self.title}>'
