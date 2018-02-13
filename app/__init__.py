# coding: utf-8

import sys
import os
from logging import FileHandler, Formatter
from dotenv import load_dotenv
from flask import Flask

# Load Upper dir
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
# set app name
app = Flask(__name__)
# Load .env
load_dotenv('.env')
# Load Config
app.config.from_object('config.CommonConfig')
# Log setting
fileHandler = FileHandler(app.config['LOG_PATH'], encoding='utf-8')
fileHandler.setFormatter(Formatter(app.config['LOG_FORMAT']))
fileHandler.setLevel(app.config['LOG_LEVEL'])
app.logger.addHandler(fileHandler)
