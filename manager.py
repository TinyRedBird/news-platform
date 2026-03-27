"""
相关配置
数据库配置
redis配置
session配置
"""
from config import Config
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

app.config.from_object(Config)

#创建SQLAlchemy对象关联app
db=SQLAlchemy(app)

#创建redis对象
redis_store= StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)

#创建session对象，读取APP中的session配置信息
Session(app)

#使用CSRFProtest保护app
CSRFProtect(app)

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    #测试redis存取数据
    redis_store.set('name','damin')
    print(redis_store.get('name'))

    #测试session存取
    session['name'] = 'tom'
    print(session.get('name'))
    return 'Hello World!'

if __name__ == '__main__':
    app.run()