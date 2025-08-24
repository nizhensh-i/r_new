#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User
import socket

def get_local_ip():
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User)

# @app.cli.command()
# def deploy():
#     db.create_all()

if __name__ == '__main__':
    app.run(host=get_local_ip(), port=5000, debug=True)