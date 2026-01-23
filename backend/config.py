import os
from urllib.parse import quote_plus, quote
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Cấu hình ứng dụng Flask"""
    
    # Database Configuration
    SQL_SERVER_DRIVER = os.getenv('SQL_SERVER_DRIVER', 'ODBC Driver 17 for SQL Server')
    SQL_SERVER_SERVER = os.getenv('SQL_SERVER_SERVER', 'localhost')
    SQL_SERVER_DATABASE = os.getenv('SQL_SERVER_DATABASE', 'OfficeCleaningService')
    SQL_SERVER_TRUSTED_CONNECTION = os.getenv('SQL_SERVER_TRUSTED_CONNECTION', 'yes')
    
    # SQLAlchemy URI
    # Hỗ trợ SQL Server Express với instance name (ví dụ: MSI\SQLEXPRESS, localhost\SQLEXPRESS)
    # Với SQLAlchemy + pyodbc, backslash trong server name cần được xử lý đặc biệt
    # Encode server name, sau đó thay thế encoded backslash (%5C) về lại backslash
    # vì pyodbc cần backslash thực sự trong connection string
    server_encoded = quote(SQL_SERVER_SERVER, safe='')
    server_encoded = server_encoded.replace('%5C', '\\')  # Giữ backslash cho instance name
    
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{server_encoded}/{SQL_SERVER_DATABASE}"
        f"?driver={quote_plus(SQL_SERVER_DRIVER)}"
        f"&Trusted_Connection={SQL_SERVER_TRUSTED_CONNECTION}"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set True để debug SQL queries
    
    # Tắt implicit returning (OUTPUT clause) vì có trigger trên bảng Users
    # SQL Server không cho phép OUTPUT clause khi có trigger enabled
    SQLALCHEMY_ENGINE_OPTIONS = {
        'implicit_returning': False
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = False  # Token không hết hạn (hoặc set thời gian)
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
