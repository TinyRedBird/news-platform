"""
相关配置
数据库配置
redis配置
session配置
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#设置配置信息
class Config(object):
    #调试信息
    DEBUG = True
    #数据库配置信息
    SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:123456@localhost:3306/info36"
    SQLALCHEMY_TRACK_MODIFICATIONS=False
app.config.from_object(Config)

#创建SQLAlchemy对象关联app
db=SQLAlchemy(app)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()