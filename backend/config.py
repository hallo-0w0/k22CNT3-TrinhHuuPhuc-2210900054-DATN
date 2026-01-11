"""
Cấu hình cho Flask Application
"""
import os
from datetime import timedelta

class Config:
    """Cấu hình cơ bản"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQL Server Database Configuration
    # Server name (ví dụ: MSI\SQLEXPRESS hoặc localhost\SQLEXPRESS)
    SQL_SERVER_SERVER = os.environ.get('SQL_SERVER_SERVER') or 'MSI\\SQLEXPRESS'
    
    # Database name
    SQL_SERVER_DATABASE = os.environ.get('SQL_SERVER_DATABASE') or 'OfficeCleaningService'
    
    # ODBC Driver (có thể là: ODBC Driver 17 for SQL Server, ODBC Driver 18 for SQL Server, SQL Server Native Client 11.0)
    SQL_SERVER_DRIVER = os.environ.get('SQL_SERVER_DRIVER') or 'ODBC Driver 17 for SQL Server'
    
    # Authentication Method: 'windows' hoặc 'sql'
    # Nếu dùng Windows Authentication, set SQL_SERVER_AUTH=windows (không cần UID/PWD)
    # Nếu dùng SQL Server Authentication, set SQL_SERVER_AUTH=sql và cung cấp UID/PWD
    SQL_SERVER_AUTH = os.environ.get('SQL_SERVER_AUTH') or 'windows'
    
    # SQL Server Authentication (chỉ dùng khi SQL_SERVER_AUTH = 'sql')
    SQL_SERVER_UID = os.environ.get('SQL_SERVER_UID') or 'sa'
    SQL_SERVER_PWD = os.environ.get('SQL_SERVER_PWD') or ''
    
    # SQLAlchemy Database URI - Tính toán connection string
    @staticmethod
    def _build_database_uri():
        """Tạo connection string động dựa trên phương thức authentication"""
        from urllib.parse import quote_plus
        
        server = os.environ.get('SQL_SERVER_SERVER') or 'MSI\\SQLEXPRESS'
        database = os.environ.get('SQL_SERVER_DATABASE') or 'OfficeCleaningService'
        driver = (os.environ.get('SQL_SERVER_DRIVER') or 'ODBC Driver 17 for SQL Server').replace(' ', '+')
        auth = os.environ.get('SQL_SERVER_AUTH') or 'windows'
        
        server_escaped = server.replace('\\', '/')  # Escape backslash cho URL
        
        if auth.lower() == 'windows':
            # Windows Authentication (Trusted Connection)
            connection_string = (
                f"mssql+pyodbc://{server_escaped}/{database}"
                f"?driver={driver}"
                f"&Trusted_Connection=yes"
            )
        else:
            # SQL Server Authentication
            uid = os.environ.get('SQL_SERVER_UID') or 'sa'
            pwd = quote_plus(os.environ.get('SQL_SERVER_PWD') or '')
            
            connection_string = (
                f"mssql+pyodbc://{uid}:{pwd}@{server_escaped}/{database}"
                f"?driver={driver}"
                f"&Trusted_Connection=no"
            )
        
        return connection_string
    
    # Gán connection string
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set True để debug SQL queries
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Kiểm tra connection trước khi sử dụng
        'pool_recycle': 3600,   # Recycle connections sau 1 giờ
    }
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CORS (nếu frontend chạy trên domain khác)
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS') or '*'
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # Member Level Configuration
    MEMBER_LEVEL_SILVER = 'SILVER'
    MEMBER_LEVEL_GOLD = 'GOLD'
    MEMBER_LEVEL_DIAMOND = 'DIAMOND'
    
    # Role Configuration
    ROLE_GUEST = 'GUEST'
    ROLE_CUSTOMER = 'CUSTOMER'
    ROLE_STAFF = 'STAFF'
    ROLE_ADMIN = 'ADMIN'

class DevelopmentConfig(Config):
    """Cấu hình cho môi trường Development"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Cấu hình cho môi trường Production"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    """Cấu hình cho môi trường Testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Dictionary mapping config names to classes
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
