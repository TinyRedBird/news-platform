"""
相关配置
数据库配置
redis配置
session配置
"""
from info import create_app, db, models
from flask_migrate import Migrate

app=create_app('develop')

#创建Manager对象管理app
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()