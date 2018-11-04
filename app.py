# encoding:utf-8

from flask import Flask, render_template, request, redirect, url_for, session
from models import User
from models import Question
from exts import db

import config

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


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
        db.session.add('question')
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/community/')
def community():
    # context = {
    #     'question': Question.query.order_by('-create_time').all()
    # }
    return render_template('community.html')


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
            return redirect(url_for('main'))
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


if __name__ == '__main__':
    app.run()
