import os
from app.models import User
from app import create_app, db
from flask_script import Manager, Shell
from werkzeug.exceptions import InternalServerError


app = create_app()
manager = Manager(app)

@app.errorhandler(InternalServerError)
def internal_server_error(e):
    print(e.code)
    print(e.name)
    print(e.description)
    return "Internal Server Error"


def make_shell_context():
    return dict(app=app, db=db, User=User)


@manager.command
def run():
    app.run(host='172.18.66.3', port=8089)


manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()