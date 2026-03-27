"""
相关配置
数据库配置
redis配置
session配置
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
app = Flask(__name__)
#设置配置信息
class Config(object):
    #调试信息
    DEBUG = True

    #数据库配置信息
    SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:123456@localhost:3306/info36"
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    #Redis配置信息
    REDIS_HOST="127.0.0.1"
    REDIS_PORT=6379

app.config.from_object(Config)

#创建SQLAlchemy对象关联app
db=SQLAlchemy(app)

#创建redis对象
redis_store= StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)

@app.route('/')
def hello_world():
    #测试redis存取数据
    redis_store.set('name','damin')
    print(redis_store.get('name'))
    return 'Hello World!'

if __name__ == '__main__':
    app.run()