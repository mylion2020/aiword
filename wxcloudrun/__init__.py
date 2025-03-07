from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql
import config

# 因MySQLDB不支持Python3，使用pymysql扩展库代替MySQLDB库
pymysql.install_as_MySQLdb()

# 创建Flask实例
app = Flask(__name__, instance_relative_config=True)
app.config['DEBUG'] = config.DEBUG

# 从配置文件加载配置
app.config.from_object('config')

# 初始化CORS
CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})

# 设定数据库链接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/ai-word'.format(config.username, config.password,
                                                                             config.db_address)

# 初始化数据库
db = SQLAlchemy(app)

# 导入视图
def init_views():
    from wxcloudrun import views
