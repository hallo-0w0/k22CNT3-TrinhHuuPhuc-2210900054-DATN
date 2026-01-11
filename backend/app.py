"""
Flask Application - Backend API
Website Thương Mại Dịch Vụ Vệ Sinh Văn Phòng
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from config import config
from datetime import datetime
import os

# Khởi tạo extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name=None):
    """Factory function để tạo Flask app"""
    
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # JWT Error Handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'Token đã hết hạn',
            'error': 'token_expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'message': 'Token không hợp lệ',
            'error': 'invalid_token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'message': 'Thiếu token xác thực',
            'error': 'authorization_required'
        }), 401
    
    # Register Blueprints
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.services import services_bp
    from routes.orders import orders_bp
    from routes.reviews import reviews_bp
    from routes.invoices import invoices_bp
    from routes.consultations import consultations_bp
    from routes.member_levels import member_levels_bp
    from routes.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(services_bp, url_prefix='/api/services')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    app.register_blueprint(invoices_bp, url_prefix='/api/invoices')
    app.register_blueprint(consultations_bp, url_prefix='/api/consultations')
    app.register_blueprint(member_levels_bp, url_prefix='/api/member-levels')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Welcome to Office Cleaning Service API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth',
                'users': '/api/users',
                'services': '/api/services',
                'orders': '/api/orders',
                'reviews': '/api/reviews',
                'invoices': '/api/invoices',
                'consultations': '/api/consultations',
                'member_levels': '/api/member-levels',
                'dashboard': '/api/dashboard'
            },
            'documentation': 'See README.md for API documentation'
        }), 200
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'API đang hoạt động',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'message': 'Endpoint không tồn tại',
            'error': 'not_found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'message': 'Lỗi server nội bộ',
            'error': 'internal_server_error'
        }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
