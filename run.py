# 创建应用实例
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wxcloudrun import app, init_views

# 初始化视图
init_views()

# 启动应用
def main():
    # 默认值
    host = '0.0.0.0'
    port = 80
    
    # 如果提供了命令行参数，则使用命令行参数
    if len(sys.argv) > 2:
        try:
            host = sys.argv[1]
            port = int(sys.argv[2])
        except (IndexError, ValueError):
            # 如果参数解析失败，使用默认值
            pass
    
    return app

if __name__ == '__main__':
    main().run(host=host, port=port)
