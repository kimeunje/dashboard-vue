# config.py
import os
from datetime import timedelta


class Config:
    """기본 설정"""

    # JWT 설정
    JWT_SECRET = os.environ.get('JWT_SECRET', 'fef#ecd@ec21@@ds-asc12!!-ke$dsy')
    TOKEN_EXPIRATION = int(os.environ.get('TOKEN_EXPIRATION', 1800))  # 30분

    # CORS 설정
    CORS_ORIGINS = [
        "http://localhost:5173", "http://10.106.25.129:5173", "http://localhost:3000",
        "http://10.106.25.129:3000"
    ]

    # 정적 파일 경로
    # STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'app', 'static')
    STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
    # TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), 'app', 'templates')
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), 'templates')

    # 로그 설정
    LOG_DIR = "logs"
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')

    # 데이터베이스 설정
    DB_CONFIG = {
        "host": os.environ.get('DB_HOST', 'localhost'),
        "port": int(os.environ.get('DB_PORT', 33060)),
        "user": os.environ.get('DB_USER', 'root'),
        "password": os.environ.get('DB_PASSWORD', 'dnb123!!'),
        "db": os.environ.get('DB_NAME', 'patch_management'),
        "charset": "utf8mb4",
    }


class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True


class ProductionConfig(Config):
    """운영 환경 설정"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


class TestConfig(Config):
    """테스트 환경 설정"""
    TESTING = True


# 환경별 설정 매핑
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
}