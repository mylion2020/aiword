# 创建应用实例
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from wxcloudrun import app

# 启动应用
if len(sys.argv) > 2:
    host = sys.argv[1]
    port = int(sys.argv[2])
else:
    host = '127.0.0.1'
    port = 5000

if __name__ == '__main__':
    app.run(host=host, port=port)
