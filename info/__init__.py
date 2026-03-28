
from config import config_dict
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

#定义全局变量
redis_store=None

def create_app(config_name):
    app = Flask(__name__)

    #根据传入配置类的名字，去除对应的配置类信息
    config = config_dict.get(config_name)
    app.config.from_object(config)

    #创建SQLAlchemy对象关联app
    db=SQLAlchemy(app)

    #创建redis对象
    global redis_store
    redis_store= StrictRedis(host=config.REDIS_HOST,port=config.REDIS_PORT,decode_responses=True)

    #创建session对象，读取APP中的session配置信息
    Session(app)

    #使用CSRFProtest保护app
    CSRFProtect(app)

    #将首页index_blue蓝图注册到app中
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)
    return app
