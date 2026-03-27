"""
相关配置
数据库配置
redis配置
session配置
"""

from flask import Flask, session
from info import create_app


app=create_app('develop')

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    # #测试redis存取数据
    # redis_store.set('name','damin')
    # print(redis_store.get('name'))
    #
    # #测试session存取
    # session['name'] = 'tom'
    # print(session.get('name'))
    return 'Hello World!'

if __name__ == '__main__':
    app.run()