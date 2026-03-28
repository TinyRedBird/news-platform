import logging

from info.modules.index import index_blue
from info import redis_store
from flask import session

@index_blue.route('/', methods=['GET', 'POST'])
def hello_world():
    #测试redis存取数据
    redis_store.set('name','damin')

    #测试session存取
    session['name'] = 'tom'
    #使用logging日志方法调试输出
    logging.info('hello world')
    logging.debug(session)
    logging.warning('hello world')
    logging.error('hello world')

    return 'Hello World!'