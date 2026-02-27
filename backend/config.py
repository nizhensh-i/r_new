import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _parse_csv_list(value):
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]

def _get_scores_year():
    raw = os.environ.get('SCORES_YEAR')
    if raw:
        try:
            return int(raw)
        except ValueError:
            return datetime.now().year
    return datetime.now().year

def _build_sqlite_uri(base_dir, year, filename='data.db'):
    db_path = os.path.join(base_dir, str(year), filename)
    return f"sqlite:///{db_path}"

SCORES_BASE_DIR = os.environ.get('SCORES_BASE_DIR') or os.path.join(BASE_DIR, 'scores')
SCORES_YEAR = _get_scores_year()
SCORES_DB_FILENAME = os.environ.get('SCORES_DB_FILENAME') or 'data.db'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USERS_PER_PAGE = 100

    SCORES_BASE_DIR = SCORES_BASE_DIR
    SCORES_YEAR = SCORES_YEAR
    SCORES_DB_FILENAME = SCORES_DB_FILENAME

    # 225软件学院, 215计算机科学与技术学院, 218先进技术研究院, 168研究生院科学岛分院
    RANKING_COLLEGE_ALLOWLIST = _parse_csv_list(
        os.environ.get('RANKING_COLLEGE_ALLOWLIST') or ''
    )
    RANKING_COLLEGE_BLOCKLIST = _parse_csv_list(
        os.environ.get('RANKING_COLLEGE_BLOCKLIST') or '225软件学院'
    )
    RANKING_COLLEGE_BLOCK_MESSAGE = os.environ.get('RANKING_COLLEGE_BLOCK_MESSAGE') or '该学院排名已关闭'

    SUPER_ADMIN_ENABLED = (os.environ.get('SUPER_ADMIN_ENABLED') or 'true').lower() in ('1', 'true', 'yes')
    SUPER_ADMIN_KAOHAO = os.environ.get('SUPER_ADMIN_KAOHAO') or '012345678912345'
    SUPER_ADMIN_PASSWORD = os.environ.get('SUPER_ADMIN_PASSWORD') or 'admin1125'
    SUPER_ADMIN_DEFAULT_COLLEGE = os.environ.get('SUPER_ADMIN_DEFAULT_COLLEGE') or ''
    SUPER_ADMIN_DEFAULT_MAJOR = os.environ.get('SUPER_ADMIN_DEFAULT_MAJOR') or ''
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or _build_sqlite_uri(
        SCORES_BASE_DIR,
        SCORES_YEAR,
        SCORES_DB_FILENAME
    )

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or _build_sqlite_uri(
        SCORES_BASE_DIR,
        SCORES_YEAR,
        SCORES_DB_FILENAME
    )


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
