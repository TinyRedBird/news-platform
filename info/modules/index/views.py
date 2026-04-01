from flask import  render_template, current_app

from info.modules.index import index_blue

@index_blue.route('/', methods=['GET', 'POST'])
def hello_world():

    return render_template('index.html')

#处理网站logo接口
@index_blue.route('/favicon.ico')
def favicon():
    #在flask中需要current_app.send_static_file(文件名)会自动去static下找
    return current_app.send_static_file('favicon.ico')