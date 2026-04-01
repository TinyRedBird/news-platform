"""
相关配置
数据库配置
redis配置
session配置
"""
from info import create_app, db
from flask_migrate import Migrate

app=create_app('develop')
import werkzeug.http
original_dump_cookie = werkzeug.http.dump_cookie

def patched_dump_cookie(*args, **kwargs):
    # 打印所有参数的类型
    print("[DEBUG] dump_cookie called with:")
    for i, arg in enumerate(args):
        print(f"  arg[{i}]: type={type(arg)}, value={arg}")
    for key, val in kwargs.items():
        print(f"  kwarg[{key}]: type={type(val)}, value={val}")
    return original_dump_cookie(*args, **kwargs)

werkzeug.http.dump_cookie = patched_dump_cookie
#创建Manager对象管理app
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()