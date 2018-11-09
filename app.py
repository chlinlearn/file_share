# encoding:utf-8

from flask import Flask, render_template, request, redirect, url_for, session
from pyhdfs import HdfsClient
# from flask_login import LoginManager,login_required
from models import User
from models import Question
from models import Answer
from exts import db

import config

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

# login_manager = LoginManager()
# login_manager.session_protection='strong'
# login_manager.login_view='login'
# login_manager.init_app(app)

# @login_manager.user_loader
# def load_user(user_id):
#   return User.get_id()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mainPage/')
def main():
    return render_template('mainPage.html')

@app.route('/question/',methods=['GET','POST'])
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title,content=content)
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        question.author=user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('community'))

@app.route('/community/')
def community():
    context = {
        'questions': Question.query.order_by('-create_time').all()
    }
    return render_template('community.html',**context)

@app.route('/detail/<question_id>/')
def detail(question_id):
    question_id = Question.query.filter(Question.id==question_id).first()
    return  render_template('detail.html',question=question_id)

@app.route('/add_amswer/',methods=['POST'])
def add_answer():
    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')

    answer = Answer(content = content,question_id=question_id)
    user_id = session.get('user_id')
    question_id = session.get('question_id')
    user = User.query.filter(User.id == user_id).first()
    answer.author = user
    question = Question.query.filter(Question.id == question_id).first()

    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail',question_id=question_id))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone, User.password == password).first()
        if user:
            session['user_id'] = user.id
            # 如果想31天内都不需要登录
            # session.permanent = True
            return redirect(url_for('index'))
        else:
            return '手机号码或者密码错误，请确认后重新登录！'


@app.route('/regist/', methods=['GET', 'POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        # 手机号码验证
        user = User.query.filter(User.telephone == telephone).first()
        # 找到了说明存在数据库中
        if user:
            return '该手机号码已经被注册，请更换手机号码注册！'
        else:
            # 判断password1和password2是否一致
            if password1 != password2:
                return '两次密码不一致，请重新输入！'
            else:
                user = User(telephone=telephone, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                # 如果注册成功，就跳转到登录页面
                return redirect(url_for('login'))


# 钩子函数
# 判断用户是否登录
@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user': user}
    return {}


# 注销，清除session
@app.route('/logout/')
def logout():
    session.pop('user_id')
    # del session('user_id')
    # session.clear()
    return redirect(url_for('login'))

#资源下载
@app.route('/all_data/')
def all_data():
    return render_template('all_data.html')

@app.route('/all_data_not_login/')
def all_data_not_login():
    return render_template('all_data_not_login.html')

#我的资源下载
@app.route('/my_data/')
def my_data():
    return render_template('my_data.html')

#下载
@app.route('/download/')
def download():
    client = HdfsClient(hosts='localhost:9870',user_name='chlinlearn')
    client.copy_to_local('/README.txt','D:\ECJTU\hadoop_files\Readme.txt')
    return redirect(url_for('all_data'))

#上传
@app.route('/upload/')
def upload():
    client = HdfsClient(hosts='localhost:9870', user_name='chlinlearn')
    client.copy_from_local('D:\ECJTU\hadoop_files\Readme.txt','/data/Readme.txt')
    return redirect(url_for('all_data'))


if __name__ == '__main__':
    app.run()
