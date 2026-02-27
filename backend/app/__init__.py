from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from config import config
import os
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'api.login'

def _ensure_sqlite_db(app):
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if not db_uri.startswith('sqlite:///'):
        return
    db_path = db_uri.replace('sqlite:///', '', 1)
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    if not os.path.exists(db_path):
        from . import models  # ensure model metadata is registered
        with app.app_context():
            db.create_all()

def create_app(config_name='default'):
    print('应用名称:', os.getenv('FLASK_APP', ''))
    print('环境：', config_name)
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    
    # 启用CORS
    CORS(app, supports_credentials=True)

    _ensure_sqlite_db(app)

    # 注册蓝图
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
