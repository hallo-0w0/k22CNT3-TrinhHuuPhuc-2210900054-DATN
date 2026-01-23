from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from backend.config import Config

# Khởi tạo extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    """Factory function để tạo Flask app"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # JWT Error Handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"JWT Expired: {jwt_payload}")
        return jsonify({'error': 'Token đã hết hạn'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"JWT Invalid Token Error: {error}")
        print(f"JWT_SECRET_KEY from config: {app.config.get('JWT_SECRET_KEY', 'NOT SET')[:20]}...")
        return jsonify({'error': f'Token không hợp lệ: {str(error)}'}), 422
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"JWT Missing Token: {error}")
        return jsonify({'error': 'Thiếu token xác thực'}), 401
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        print(f"JWT Needs Fresh Token: {jwt_payload}")
        return jsonify({'error': 'Token cần được làm mới'}), 401
    
    # Register blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.services import services_bp
    from backend.routes.orders import orders_bp
    from backend.routes.content import content_bp
    from backend.routes.admin import admin_bp
    from backend.routes.staff import staff_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(services_bp, url_prefix='/api/services')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(content_bp, url_prefix='/api/content')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    
    return app
