
from info import create_app, db
from flask_migrate import Migrate
import sqlalchemy
app=create_app('develop')

#创建Manager对象管理app
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()