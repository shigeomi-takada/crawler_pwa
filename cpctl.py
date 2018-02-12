#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fire
import sys
import os
import pickle
import gzip
import time
import pytz
from multiprocessing import Process
from datetime import datetime, timedelta

from app.core.crawler import Crawler

class Cpctl:
    '''
    spam_apiで定期的に発生する処理をまとめているクラス
    fireモジュールを使っているので、CLIとして実行することができる
    e.g. python spctl.py ready_datasets --key_name=spam:ds:msg:pos --obj_type=msg
    実行すると永続的に起動し続けるコマンドは run_ をつけるようにしている

    Run command example
    python spctl.py ready_datasets --key_name=spam:ds:tmp:msg:pos

    '''

    def launch(self, url):
        '''
        python cpctl.py launch --url=https://www.example.com
        '''
        Crawler().launch(url)

    def run(self):
        ''''''
        Crawler().run()

if __name__ == '__main__':
  fire.Fire(Cpctl)
