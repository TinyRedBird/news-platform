"""
相关配置
数据库配置
redis配置
session配置
"""

from datetime import timedelta
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session

app = Flask(__name__)
#设置配置信息
class Config(object):
    #调试信息
    DEBUG = True
    SECRET_KEY = '1jn242HB1HJ8BHJVhn55hj'

    #数据库配置信息
    SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:123456@localhost:3306/info36"
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    #Redis配置信息
    REDIS_HOST="127.0.0.1"
    REDIS_PORT=6379

    #Session配置信息
    SESSION_TYPE = 'redis'
    SESSION_REDIS=StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER=True #设置签名存储
    PERMANENT_SESSION_LIFETIME=timedelta(seconds=3)

app.config.from_object(Config)

#创建SQLAlchemy对象关联app
db=SQLAlchemy(app)

#创建redis对象
redis_store= StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)

#创建session对象，读取APP中的session配置信息
Session(app)

@app.route('/')
def hello_world():
    #测试redis存取数据
    redis_store.set('name','damin')
    print(redis_store.get('name'))

    #测试session存取
    session['name'] = 'z'
    print(session.get('name'))
    return 'Hello World!'

if __name__ == '__main__':
    app.run()