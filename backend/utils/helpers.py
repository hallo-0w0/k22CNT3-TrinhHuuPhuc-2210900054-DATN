"""
Helper functions
"""
from flask import request
from app import db
from models.activity_log import ActivityLog
from models.user import User

def create_activity_log(user_id, action_type, entity_type=None, entity_id=None, description=None):
    """
    Tạo log hoạt động
    
    Args:
        user_id: ID người dùng
        action_type: Loại hành động (CREATE, UPDATE, DELETE, LOGIN, LOGOUT)
        entity_type: Loại entity (Order, User, Service, v.v.)
        entity_id: ID entity
        description: Mô tả chi tiết
    """
    try:
        log = ActivityLog(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating activity log: {e}")

def paginate_query(query, page=1, per_page=20):
    """
    Phân trang query
    
    Args:
        query: SQLAlchemy query object
        page: Số trang (bắt đầu từ 1)
        per_page: Số items mỗi trang
    
    Returns:
        dict với items, total, page, pages, per_page
    """
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': pagination.per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }

def calculate_discount_price(base_price, member_level):
    """
    Tính giá sau giảm giá dựa trên member level
    
    Args:
        base_price: Giá gốc
        member_level: MemberLevel object hoặc None
    
    Returns:
        tuple (discount_percentage, discount_amount, final_price)
    """
    if not member_level:
        return 0, 0, base_price
    
    discount_percentage = float(member_level.discount_percentage) if member_level.discount_percentage else 0
    discount_amount = base_price * (discount_percentage / 100)
    final_price = base_price - discount_amount
    
    return discount_percentage, discount_amount, final_price

def calculate_member_level_priority(member_level_code):
    """
    Tính độ ưu tiên dựa trên member level
    
    Args:
        member_level_code: Mã member level (SILVER, GOLD, DIAMOND)
    
    Returns:
        int: Độ ưu tiên (0, 1, 2)
    """
    priority_map = {
        'SILVER': 0,
        'GOLD': 1,
        'DIAMOND': 2
    }
    return priority_map.get(member_level_code, 0)
