import logging

from redis import StrictRedis
from datetime import timedelta

#设置配置信息
class Config(object):
    #调试信息
    DEBUG = True
    SECRET_KEY = '1jn242HB1HJ8BHJVhn55hj'

    #数据库配置信息
    SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:123456@localhost:3306/news"
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    #Redis配置信息
    REDIS_HOST="127.0.0.1"
    REDIS_PORT=6379

    #Session配置信息
    SESSION_TYPE = 'redis'
    SESSION_REDIS=StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER=True #设置签名存储
    PERMANENT_SESSION_LIFETIME=timedelta(seconds=3)
    #默认日志级别
    LEVE_NAME=logging.DEBUG

#开发环境配置信息
class DevelopConfig(Config):
    pass

#生产（线上）环境配置信息
class ProductConfig(Config):
    LEVE_NAME=logging.ERROR
    DEBUG = False

#测试环境配置信息
class TestConfig(Config):
    pass

#提供一个统一的访问入口
config_dict={
    'develop':DevelopConfig,
    'product':ProductConfig,
    'test':TestConfig
}