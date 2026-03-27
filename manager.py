"""
相关配置
数据库配置
redis配置
session配置
"""

from flask import Flask, session
from info import create_app

app=create_app('develop')

if __name__ == '__main__':
    app.run()