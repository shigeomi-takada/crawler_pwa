# coding: utf-8

import os
import logging

from app import app


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

    # UA List
    with open('storage/ua.txt', 'r') as f:
        UA_LISTS = [line.rstrip('\n') for line in f.readlines()]

    URL_PATTERN = r"https?:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+"

    # LOG
    # Log format is LTSV
    # Ref: http://flask.pocoo.org/docs/0.12/errorhandling/#complex-log-formatting
    LOG_PATH = 'logs/app.log'
    LOG_FORMAT = 'time:%(asctime)s\tlevel:%(levelname)s\tfile:%(filename)s\tmodule:%(module)s\tmethod:%(funcName)s\tline:%(lineno)d\tmessage:%(message)s'

    # List
    URLS = 'cp:urls'
    URLS_BACKUP = 'cp:urls:backup'
