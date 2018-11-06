#encoding: utf-8
#@author:xuchunlin
#@time:2018/11/3 12:44
#@filename:manage.py

from flask_script import Manager
# from flask_login import LoginManager,login_required
from flask_migrate import Migrate,MigrateCommand
from app import app
from exts import db
from models import User
from models import Answer
from models import Question

manager = Manager(app)
#设置未登录跳转到登录界面


#使用Migrate绑定app,db
migrate = Migrate(app,db)

#添加迁移脚本的命令到manager中
manager.add_command('db',MigrateCommand)


if __name__ == "__main__":
    manager.run()