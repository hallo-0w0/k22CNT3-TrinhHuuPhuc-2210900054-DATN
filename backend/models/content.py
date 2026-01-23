from backend import db
from datetime import datetime

class Content(db.Model):
    """Bảng Content"""
    __tablename__ = 'Content'
    
    content_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content_type = db.Column(db.NVARCHAR(50), nullable=False)  # HOME, ABOUT, FAQ, NEWS, BANNER
    title = db.Column(db.NVARCHAR(255), nullable=False)
    content_text = db.Column(db.Text)
    image_url = db.Column(db.NVARCHAR(500))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_contents')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_contents')
    
    def to_dict(self):
        return {
            'content_id': self.content_id,
            'content_type': self.content_type,
            'title': self.title,
            'content_text': self.content_text,
            'image_url': self.image_url,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
