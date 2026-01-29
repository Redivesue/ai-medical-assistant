from . import create_app

# uvicorn 启动时会使用到的全局应用实例：
#   uvicorn app.main:app --reload
app = create_app()

