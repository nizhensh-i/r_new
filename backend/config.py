import os

def _parse_csv_list(value):
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USERS_PER_PAGE = 100

    # 225软件学院, 215计算机科学与技术学院, 218先进技术研究院, 168研究生院科学岛分院
    RANKING_COLLEGE_ALLOWLIST = _parse_csv_list(
        os.environ.get('RANKING_COLLEGE_ALLOWLIST') or '215计算机科学与技术学院,218先进技术研究院,168研究生院科学岛分院'
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
    SQLALCHEMY_DATABASE_URI = 'sqlite:////Users/nizhenshi/Documents/proj/rank_new/backend/scores/2026/data.db'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:////home/ustc/data.db'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
