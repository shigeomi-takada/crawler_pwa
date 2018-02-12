# coding: utf-8

import re
import os
import requests
import pytz
import time
import json
import random
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from multiprocessing import Process

from app import app
from app.mysql.urls import Urls
from app.redis.connect import Connect


class Crawler():
    '''
    spam messagesには80%以上の確率でurlが含まれる。
    url関連の処理は当classにまとめる
    '''

    def __init__(self):
        ''''''


    def _request_url(self, url):
        '''
        特定のURLのテキストデータをリクエストして取得する
        5.0秒以上経っても返ってこないレスポンスは無視
        @param str url
        @return str
        '''
        headers = app.config['HEADERS']
        headers['User-Agent'] = random.choice(app.config['UA_LISTS'])
        try:
            r = requests.get(
                url,
                timeout=3.0,
                headers=headers,
                allow_redirects=True)
        # 指定時間以上経過してもレスポンスが返ってこない場合
        except requests.exceptions.ConnectTimeout as e:
            app.logger.info(e)
            return ''
        # 何かしらの例外が発生した場合
        except Exception as e:
            app.logger.info(e)
            return ''

        if r.status_code == 404:
            app.logger.info('status_code: {0} url: {0} is not found'.format(
                r.status_code, url))
            return ''

        if r.status_code >= 300:
            app.logger.info('status_code: {0} url: {1} Somethig is wrong'.format(
                r.status_code, url))
            return ''

        return r.text

    def _extract_pwa(self, soup):
        '''
        PWAページには必ず、以下のメタタグがあるものとする
        <link rel="manifest" href="/manifest.json" />
        manifest.jsonは必ずしもmanifest.jsonという名前でなくても良い模様
        :param <class 'bs4.BeautifulSoup'> soup
        :return bool
        '''
        links = soup.find_all('link')
        for link in links:
            if link.get('rel') == 'manifest':
                return True

        return False

    def _filter_url(self, url):
        '''
        不要なデータを取り除く
        :param str url
        :return str
        '''
        url_parsed = urlparse(url)

        # 空の場合
        # 例えば、<a>をbuttonとして使っているような場合は空になる
        if not url_parsed:
            return ''

        if url_parsed[0] not in ['http', 'https']:
            return ''

        # 内部リンクジャンプの場合
        if url_parsed[5]:
            return ''

        # たまにbytes型が入っていることがあるので、チェック。orは左から評価が走る
        if isinstance(url_parsed[2], bytes):
            return ''

        # javascript:void(0)の場合
        if 'javascript' in url_parsed[1] or 'javascript' in url_parsed[2]:
            return ''

        return url

    def _extract_href(self, soup):
        '''
        <a>タグ内のhref属性を全て取得し、listで返す
        :param <class 'bs4.BeautifulSoup'> soup
        :return set
            重複を消すためにset型にしている
        '''

        # 重複したurlが1つのページに含まれることは多々あるのでset型にする
        hrefs = set([])

        # 存在しない場合は空のlistを返す
        links = soup.find_all('a')

        if not links:
            return hrefs

        for link in links:
            try:
                url = self._filter_url(link.get('href'))
                if url:
                    hrefs.add(url)
            except KeyError as e:
                app.logger.info(e)
                print(e)
                continue

        return hrefs

    def _extract_main_netloc(self, hrefs):
        '''
        与えられたhrefs引数に最も多く含まれるnetlocをとして抽出する
        :param list
        :return str
        '''
        links = {}

        for href in hrefs:
            href = urlparse(href)

            if not href[1]:
                continue

            host = href[0]+'://'+href[1]

            if host not in links:
                links[host] = 1
            else:
                links[host]+=1

        hrefs_sorted = [url for url, count in sorted(
            links.items(),
            key=lambda x:x[1], reverse=True)]

        return hrefs_sorted[0]

    def _join_relative_path(self, hrefs, scheme, netloc):
        '''
        netlocがなく、pathがあるものは、相対URLとみなし、絶対URLに変換する
        :param list hrefs
        :param str netloc
        :return list
        '''

        scheme_netloc = scheme + '://' + netloc

        links = []
        for href in hrefs:
            href_parsed = urlparse(href)

            # netlocがある場合はそのままで良い
            if href_parsed[1]:
                links.append(href)

            # netlocが空で、pathが存在する場合
            if not href_parsed[1] and href_parsed[2]:
                links.append(urljoin(scheme_netloc, href))

        return links

    def _extract_different_urls(self, links, netloc):
        '''
        linksの中にnetloc以外のドメインがあれば抽出する
        :param list links
        :param str netloc
        :return list
        '''
        return [link for link in links if urlparse(link)[1] != netloc]

    def _filter_urls_exists(self, urls):
        '''
        DBに保存されていないもののみを抽出して返す
        :param list
        :return list
        '''
        with Urls() as m:
            return [url for url in urls if not m.is_exist(urlparse(url)[1])]

    def _save(self, now, scheme, netloc, path, pwa, urls_external):
        '''
        :return int
        '''

        if scheme == 'http':
            scheme = 0
        elif scheme == 'https':
            scheme = 1
        else:
            app.logger.info('scheme is not http or https. scheme is {0}'.format(scheme))
            return 0

        with Urls() as m:

            if not m.is_exist(netloc):
                url_object_id = m.add({
                    'datetime': now,
                    'scheme': scheme,
                    'netloc': netloc,
                    'path': path,
                    'pwa': pwa,
                    'urls_external': json.dumps(urls_external)
                })

        if urls_external:
            with Connect().open().pipeline(transaction=False) as pipe:
                pipe.lpush(app.config['URLS'], *urls_external)
                pipe.execute()

        return 1

    def _start(self, url):
        '''

        '''
        url_parsed = urlparse(url)

        if not url_parsed[1]:
            return None

        text = self._request_url(url)

        if not text:
            return None

        print(url)

        soup = BeautifulSoup(text, "lxml")
        hrefs = self._extract_href(soup)
        pwa = self._extract_pwa(soup)

        links = self._join_relative_path(hrefs, url_parsed[0], url_parsed[1])
        urls_diff = self._extract_different_urls(links, url_parsed[1])
        urls_diff_new = self._filter_urls_exists(urls_diff)

        now = datetime.now(pytz.timezone('Asia/Tokyo')).strftime("%Y-%m-%d %H:%M:%S")

        url_object_id = self._save(
            now,
            url_parsed[0],
            url_parsed[1],
            url_parsed[2],
            pwa,
            urls_diff_new)

        if url_object_id:
            app.logger.info('id: {0}, pwa: {1}, url: {2}'.format(
                url_object_id, pwa, url))

    def launch(self, url):
        '''
        redisにurlが空の場合は当メソッドを呼び出すこと
        :param str url
        '''
        self._start(url)
        r = Connect().open()
        urls = r.lrange(app.config['URLS'], 0, -1)
        print('{0} urls are pushed.'.format(len(urls)))

    def run(self):
        '''

        '''
        app.logger.info('run_crawler start')

        r = Connect().open()
        while True:
            url = r.rpoplpush(app.config['URLS'], app.config['URLS_BACKUP'])
            if not url:
                app.logger.info('Url is empty. Loop has been done.')
                print('url is empty. Loop has been done.')
                break
            p = Process(target=self._start, args=(url,))
            p.start()
            p.join()
