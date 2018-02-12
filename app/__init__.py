# coding: utf-8

import sys
import os

from raven.contrib.flask import Sentry
from logging import FileHandler, Formatter
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

# 上の階層を参照できるようにする
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

# 引数はアプリケーションのモジュール名
app = Flask(__name__)

# 環境によって異なる設定は.envから読み込む
# envファイルの値はload_dotenvで読み込むことで、以降から次のように参照することができる
# os.environ.get('ENVIRONMENT')
load_dotenv('.env')

# 全環境で共通の設定はconfig.pyから読み込む
app.config.from_object('config.CommonConfig')

# logging引数が期待通りに動かないぞ!!?
if os.environ.get('ENVIRONMENT') == 'production':
    sentry_logging = True
else:
    sentry_logging = False
sentry = Sentry(dsn=os.environ.get('SENTRY_DSN'))
sentry.init_app(app, logging=sentry_logging)
app.sentry = sentry

# Log関連の設定
fileHandler = FileHandler(app.config['LOG_PATH'], encoding='utf-8')
fileHandler.setFormatter(Formatter(app.config['LOG_FORMAT']))
fileHandler.setLevel(app.config['LOG_LEVEL'])
app.logger.addHandler(fileHandler)

# 第二引数にアクセス先を制限する値を持たせることもできる
CORS(app)
