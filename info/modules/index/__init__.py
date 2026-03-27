from flask import Blueprint

#创建蓝图对象
index_blue = Blueprint('index', __name__)


#导入views文件装饰图函数 .表示当前模块下
from . import views