# encoding:utf-8

from flask import Flask, render_template, request, redirect, url_for, session,g,flash
from pyhdfs import HdfsClient
from sqlalchemy import or_
from flask_login import LoginManager,login_required,login_manager
from models import User
from models import Question
from models import Answer
from models import File
from exts import db
import os


import config

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

#登录状态控制
login_manager = LoginManager()
login_manager.session_protection = 'Strong' #级别
login_manager.login_message = u"Please login"#消息闪烁提醒
login_manager.login_message_category = "info"
login_manager.login_view = 'login'  #登录函数路径

login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    #回调函数
    return User.query.get(user_id)


# @app.route('/')
# def index():
#     return render_template('index.html')
@app.route('/')
@app.route('/mainPage/')
def mainPage():
    return render_template('mainPage.html')

@app.route('/question/',methods=['GET','POST'])
@login_required
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
    question_model = Question.query.filter(Question.id==question_id).first()
    return  render_template('detail.html',question=question_model)

@app.route('/search/')
def search():
    #模糊查找，按文件名，格式匹配
    q = request.args.get('q')
    context = {
        'files': File.query.filter(or_(File.filename.contains(q),File.id.contains(q),File.type.contains(q))).all()
    }
    return render_template('all_data.html',**context)

@app.route('/add_amswer/',methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')

    answer = Answer(content = content)
    user_id = session.get('user_id')
    #question_id = session.get('question_id')
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
        user = User.query.filter(User.telephone == telephone).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            # 如果想31天内都不需要登录
            # session.permanent = True
            return redirect(url_for('mainPage'))
        else:
             return '手机号码或者密码错误，请确认后重新登录！'
           # return jsonify({'status':'-1','errmsg':'用户名或密码错误！'})

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
    if hasattr(g,'user'):
        return {'user': g.user}
    return {}

@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id==user_id).first()
        if user:
            g.user=user



# 注销，清除session
@app.route('/logout/')
def logout():
    session.pop('user_id')
    # del session('user_id')
    # session.clear()
    return redirect(url_for('mainPage'))

#资源下载
@app.route('/all_data/',methods=['GET','POST'])
@login_required
def all_data():
    context = {
        'files': File.query.all()
    }
    return render_template('all_data.html',**context)

@app.route('/all_data_not_login/')
def all_data_not_login():
    context = {
        'files': File.query.all()
    }
    return render_template('all_data_not_login.html',**context)

#我的资源下载
@app.route('/my_data/')
@login_required
def my_data():
    return render_template('my_data.html')

#下载
@app.route('/download/<file_id>/',methods=['GET','POST'])
@login_required
def download(file_id):
    f = File.query.get(file_id)
    #print(f.filename)
    distpath = '/files/'+f.filename
    localpath = 'D:\\ECJTU\\hadoop_files\\download\\'+f.filename
    client = HdfsClient(hosts='localhost:9870',user_name='chlinlearn')
    client.copy_to_local(distpath, localpath)
    if f:
        message = "下载成功"
        return redirect(url_for('all_data',message=message))
    else:
        message = "下载失败，请重试"
        return redirect(url_for('all_data', message=message))
#上传
@app.route('/upload/',methods=['POST'])
@login_required
def upload():
    if request.method=='POST':
        f = request.files['filename']
        #获取文件大小
        size = len(f.read())/1024
        #获取文件名
        filename = os.path.split(f.filename)[1]
        #获取文件后缀名
        type = os.path.splitext(f.filename)[1]

        print(filename)
        print(size)
        print(os.path.splitext(f.filename)[1])
        #print(file) #读取的是文件，不是文件名
        #filename = secure_filename(file.filename)

        localpath = 'D:\\ECJTU\\hadoop_files\\upload\\'+filename #本地路径
        distpath = '/files/'+filename #分布式文件系统路径
        client = HdfsClient(hosts='localhost:9870', user_name = 'chlinlearn')
        client.copy_from_local(localpath,distpath)

        #添加信息到数据库
        file = File(filename=filename,type=type,size=size)
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        file.author = user
        db.session.add(file)
        db.session.commit()
        return redirect(url_for('all_data'))

if __name__ == '__main__':
    app.run()
