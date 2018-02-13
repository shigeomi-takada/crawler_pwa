# -*- coding: utf-8 -*-

import fire
from app.core.crawler import Crawler


class Cpctl:
    '''
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
