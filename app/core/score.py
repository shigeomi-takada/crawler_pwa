# coding: utf-8

import json
import random
import requests
import subprocess
from multiprocessing import Pool

from app import app
from app.mysql.urls import Urls
from app.mysql.scores import Scores
from app.redis.connect import Connect


class Score():
    '''
    lighthouseを使ってPWAサイトをスコアリングする
    lighthouseを実行すると10000行以上出力されるが、利用するのは以下の値だけで良い
    {
        'reportCategories': [
            {
                'id': "performance",
                'score': 29.235294117647058
            },
            {
                'id': "pwa",
                'score': 90.9090909090909
            },
            {
                'id': "accessibility",
                'score': 76.53061224489795
            },
            {
                'id': "best-practices",
                'score': 100
            },
            {
                'id': "seo",
                'score': 90
            }
        ]
    }
    '''

    def _add(self, score):
        ''''''
        with Scores() as m:
            score_id = m.add({
                'url_id': score['url_id'],
                'is_ssl': score['is_ssl'],
                'performance': score['performance'],
                'pwa': score['pwa'],
                'accessibility': score['accessibility'],
                'best_practice': score['best_practice'],
                'seo': score['seo']
            })

        return score_id

    def _is_ssl(self, url):
        '''
        sslに対応していないページにhttpsでアクセスすると停止するようなので
        lighthouseを起動する前にrequestsでSSLに対応しているかチェックする
        '''
        headers = app.config['HEADERS']
        headers['User-Agent'] = random.choice(app.config['UA_LISTS'])
        try:
            res = requests.get(
                url,
                headers=headers,
                verify=True)
        except requests.exceptions.SSLError as e:
            return False

        if res.status_code == 200:
            return True
        else:
            return False

    def _lighthouse(self, url):
        '''
        :param dict url
        :return None
        '''

        with Scores() as s:
            is_exist = s.is_exist(url['id'])

        if is_exist >= 1:
            return None

        url_access = 'https://' + url['netloc']

        # SSL対応チェック
        is_ssl = self._is_ssl(url_access)

        if not is_ssl:
            self._add({
                'url_id': url['id'],
                'is_ssl': 0,
                'performance': 0,
                'pwa': 0,
                'accessibility': 0,
                'best_practice': 0,
                'seo': 0
            })
            app.logger.info('Failed: SSL Error, url: {0}'.format(url_access))
            return None

        try:
            res_process = subprocess.run(
                ["lighthouse", url_access, "--quiet", "--output", "json"],
                stdout=subprocess.PIPE)
        except Exception as e:
            app.logger.info(e)
            app.logger.info('Failed, url: {0}'.format(url_access))
            return None

        if res_process.returncode != 0:
            app.logger.info('Failed, url: {0}'.format(url_access))
            self._add({
                'url_id': url['id'],
                'is_ssl': 1,
                'performance': 0,
                'pwa': 0,
                'accessibility': 0,
                'best_practice': 0,
                'seo': 0
            })
            return None

        s = res_process.stdout.decode()
        s = json.loads(s)
        categories = s['reportCategories']
        # 順番が固定されていることを前提とする
        score = [category['score'] for category in categories]

        score_id = self._add({
            'url_id': url['id'],
            'is_ssl': 1,
            'performance': score[0],
            'pwa': score[1],
            'accessibility': score[2],
            'best_practice': score[3],
            'seo': score[4]
        })

        print('Success, url: {0}, score_id:{1}'.format(
            url_access,
            score_id))

    def run(self):
        ''''''
        with Urls() as m:
            pwas = m.get_pwas()

        with Pool() as pool:
            pool.map(self._lighthouse, pwas, chunksize=1000)
