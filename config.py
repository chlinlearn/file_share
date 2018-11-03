#encoding: utf-8
#@author:xuchunlin
#@time:2018/11/3 12:24
#@filename:config.py

import os

DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'root'
PASSWORD = '1234'
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'file_share'

DB_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT,DRIVER,USERNAME,PASSWORD,HOST,PORT,DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = DB_URI

DEBUG = True
SECRET_KEY = os.urandom(24)