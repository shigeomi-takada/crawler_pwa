# coding: utf-8

import os
import logging

from app import app

# Flaskの標準設定一覧
# http://flask.pocoo.org/docs/0.12/config/

# 設定値ファイル
# 次のように読み込むとことができる
# app.config.from_object('config.BaseConfig')
# 参照するときは次のようにする
# app.config['USERNAME']


class CommonConfig(object):
    ENVIRONMENT = os.environ.get('ENVIRONMENT')

    if ENVIRONMENT == 'development':
        DEBUG = True
        app.logger.setLevel(logging.DEBUG)
        LOG_LEVEL = logging.DEBUG
    else:
        DEBUG = False
        app.logger.setLevel(logging.INFO)
        LOG_LEVEL = logging.INFO

    JSON_AS_ASCII = False

    # For scraping headers
    HEADERS = {
        'Accept-Language': 'en-US'
    }

    # UR List
    with open('storage/ua.txt', 'r') as f:
        UA_LISTS = [line.rstrip('\n') for line in f.readlines()]

    URL_PATTERN = r"https?:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+"

    # LOG
    # Log format is LTSV
    # Ref: http://flask.pocoo.org/docs/0.12/errorhandling/#complex-log-formatting
    LOG_PATH = 'logs/app.log'
    LOG_FORMAT = 'time:%(asctime)s\tlevel:%(levelname)s\tfile:%(filename)s\tmodule:%(module)s\tmethod:%(funcName)s\tline:%(lineno)d\tmessage:%(message)s'

    # Multiprocessing
    cpu_count = os.cpu_count()
    if ENVIRONMENT == 'development':
        POOL_PROCESS_NUM = os.cpu_count()
    elif cpu_count == 1:
        POOL_PROCESS_NUM = 1
    else:
        POOL_PROCESS_NUM = cpu_count - 1

    # List
    URLS = 'cp:urls'
    URLS_BACKUP = 'cp:urls:backup'
