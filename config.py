import os

# 是否开启debug模式
DEBUG = True

# 读取数据库环境变量
# username = os.environ.get("MYSQL_USERNAME", 'root')
# password = os.environ.get("MYSQL_PASSWORD", '111111')
# db_address = os.environ.get("MYSQL_ADDRESS", '127.0.0.1:3306')

username = os.environ.get("MYSQL_USERNAME", 'mylion')
password = os.environ.get("MYSQL_PASSWORD", 'Aa111111')
db_address = os.environ.get("MYSQL_ADDRESS", '10.15.101.169:3306')

# 数据库配置
SQLALCHEMY_DATABASE_URI = f'mysql://{username}:{password}@{db_address}/ai-word'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 跨域支持
CORS_ORIGINS = ['*']

# 应用配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_123456')
