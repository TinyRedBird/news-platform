from info.modules.index import index_blue

@index_blue.route('/', methods=['GET', 'POST'])
def hello_world():
    # #测试redis存取数据
    # redis_store.set('name','damin')
    # print(redis_store.get('name'))
    #
    # #测试session存取
    # session['name'] = 'tom'
    # print(session.get('name'))
    return 'Hello World!'