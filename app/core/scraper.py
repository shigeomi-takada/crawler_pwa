# coding: utf-8

import re
import os
import requests
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

from app import app
from app.mysql.messages import Messages
from app.redis.connect import Connect


class Scraper():
    '''
    spam messagesには80%以上の確率でurlが含まれる。
    url関連の処理は当classにまとめる
    '''

    def __init__(self):
        ''''''


    def _request_url(self, url, allow_redirects=True):
        '''
        特定のURLのテキストデータをリクエストして取得する
        5.0秒以上経っても返ってこないレスポンスは無視
        @param str url
        @param bool allow_redirects
            301が返ってきたときに自動的にそのurlへリダイレクトするか否か。
        @return str
        '''
        try:
            r = requests.get(
                url,
                timeout=5.0,
                headers=app.config['HEADERS'],
                allow_redirects=allow_redirects)

        # 3秒以上経過してもレスポンスが返ってこない場合
        except requests.exceptions.ConnectTimeout as e:
            app.sentry.captureException()
            return ''
        # 何かしらの例外が発生した場合
        except:
            app.sentry.captureException()
            return ''

        if r.status_code == 404:
            return ''

        if r.status_code >= 400:
            app.sentry.captureMessage('スクレイピングでエラーが返ってきた。なぜだ!? status: {0}, url: {1}'.format(r.status_code, url))
            return ''

        return r.text

    def _extract_href_short_google(self, url):
        '''
        goo.glの短縮URLサービスのために、リダイレクトページを挟んでいるページのURLを取得する
        goo.gl以外にも http://bit.ly/2xX9hPB などの短縮URLは存在するが、大抵、200番が
        返ってきてrequestsが適切に対処できないので、goo.glだけ対応する
        @param str url
        @return str
        '''
        # allow_redirects:
        # 301が返ってきた時に自動的に指定されたリダイレクト先のURLへ遷移するか否か
        text = self._request_url(url, allow_redirects=False)
        if not text:
            return ''

        href = self._extract_href(text)

        # hrefが存在しないということはあり得ないが念のため
        if not href:
            return ''

        # goo.glのページに含まれるURLは必ず1つである
        return href[0]

    def _parse_url(self, url):
        '''
        @param str url
        @return str
        '''
        # '//' で始まる場合にのみ netloc を認識する。それ以外の場合は、
        # 入力は相対URLであると推定され、path 部分で始まることになる
        url_parse = urlsplit(url)
        if not url_parse.netloc:
            return ''

        # 末尾に ) が混ざることが多々あるので取り除く
        if not url_parse.path:
            path = ''
        elif url_parse.path[-1] == ')':
            path = url_parse.path[0:-1]
        else:
            path = url_parse.path

        if url_parse.query:
            query = '?' + url_parse.query
        else:
            query = ''

        return url_parse.scheme + '://' + url_parse.netloc + path + query

    def _extract_href(self, text):
        '''
        htmlエレメントの中か<a>タグのhref属性を全て取得する
        @param <class 'bs4.element.ResultSet'> _retrieve_url()の返り値を渡すこと
        @return list
            href属性の値、つまり、urlをlistでまとめて返す。存在しなければ空のlistを返す
        '''

        soup = BeautifulSoup(text, "lxml")
        # <body>タグ内の<a>タグを全て取得する
        # 存在しない場合は空のlistを返す
        aa = soup.body.find_all('a')

        if not aa:
            return []

        # <a>タグのhref属性を全て取得する
        href = []
        try:
            for a in aa:
                # http(s)で始まるもののみを選別する
                # 選別しないと相対パスやjavascript:void(0);とかが結構混ざってくる
                url = self._parse_url(a['href'])
                if url:
                    href.append(url)
        # <a>タグがあるにも関わらず、href属性がない場合はスキップ
        except KeyError as e:
            pass

        return href

    def _find_url(self, url):
        '''
        ブラックリストとして登録しているURLが含まれるかを探す
        @param str url List形式でurlを渡す
        @return str
            見つけたらそのurlを返す。なければ空の文字列を返す
        '''
        url_parsed = self._parse_url(url)

        # urlの形式ではなければ、空の文字列を返す
        if not url_parsed:
            return ''

        for url_black in self.urls_black:
            if url_parsed == url_black:
                return url_parsed

        # 該当するものがなければ空の文字列を返す
        return ''

    def __find_keyword(self, text):
        '''

        キーワードで見分けるのは有効ではないことがわかったのでこのメソッドは使わない

        htmlエレメントの中からブラックリストとして登録しているキーワードが含まれるかをチェックする
        大文字・小文字を区別しない
        @param <class 'bs4.element.ResultSet'> _request_url()の返り値を渡すこと
        @return list
            キーワードが見つかればその文字列を返す
        '''
        soup = BeautifulSoup(text, "lxml")

        # <body>タグ内に調べたい文字列があるか調べる
        # Listで返る。なければ空のListが返る。
        # e.g. [' LINE ID ', ' LINE', 'TwitterLine', 'Facebookline'] | []
        keywords = soup.body.find_all(text=re.compile(
            app.config['PATTERN_BLACKLIST_KEYWORDS_COMPILE'], re.IGNORECASE))

        if not keywords:
            return []

        # ' LINE ID 'こんな感じに前後にスペースが入っているケースが多いので
        # strip関数を挟んでもう一度検索する
        # また、onlineこういうのも抽出してしまうので、ここでもう一度検索し直す
        texts = []
        for keyword in keywords:
            m = re.search(app.config['PATTERN_BLACKLIST_KEYWORDS_SEARCH'],
                keyword.strip(),
                re.IGNORECASE)
            if m:
                texts.append(m.group(0))

        return texts

    def add_url_blacklist(self, url):
        '''
        url_blacklistにurlを追加する
        Set型を採用しているので、重複の心配はない
        @return int
        '''
        url = self._parse_url(url)
        if not url:
            return 0

        self.r.sadd(app.config['URL_BLACKLIST'], url)

    def add_url_blacklist_for_batch(self, min_datetime=None):
        '''
        blacked判定されたユーザのメッセージからurlを全て抜き出し、Redisに保存
        @return int
        '''
        if min_datetime is None:
            # まず消す
            self.r.delete(app.config['URL_BLACKLIST'])

            # blackedユーザのmessageを全て取得
            with Messages(role='slave') as m:
                messages = m.get_pos()
        else:
            # blackedユーザのmessageを全て取得
            with Messages(role='slave') as m:
                messages = m.get_pos(min_datetime=min_datetime)

        # 各メッセージからurlを抜き出し、セット
        urls = []
        for msg in messages:
            url_extract = self.extract_url(msg['description'].decode('utf-8'))
            if url_extract:
                urls.extend(url_extract)

        urls_pos = []
        urls_google = []

        for url in urls:
            # 対象にしないurlたち
            if self._filter_url(url):
                continue

            # goo.gl短縮URLの場合は本来のURLを抽出
            if 'goo.gl' in url:
                urls_google.append(url)
            else:
                urls_pos.append(url)

        # set型に変換することで重複しているurlを消す
        urls_pos = set(urls_pos)
        urls_google = set(urls_google)

        urls_google_original = []
        for url in urls_google:
            url_original = self._extract_href_short_google(url)
            if url_original:
                if self._filter_url(url_original):
                    continue
                urls_google_original.append(url_original)

        # set型に変換することで重複しているurlを消し、urls_posと連結
        urls_last = urls_pos.union(set(urls_google_original))

        for url in urls_last:
            self.add_url_blacklist(url)

        if os.environ.get('ENVIRONMENT') == 'development':
            count = Connect(role='slave').open().scard(app.config['URL_BLACKLIST'])
            print('URL_BLACKLISTの数: {0} 個のurlをsaddした'.format(str(count)))

    def run(self, body):
        '''
        @param str body
            messageのdescriptionを渡せば良い
            decode()でstr型に変換してから渡すこと
        @return dict, bool
        '''

        # メッセージの本文からurlを抜き出す
        # @return list
        urls = self.extract_url(body)

        is_black_url = False

        # bodyにurlが含まれなければ終了
        if not urls:
            return {
                'url': {
                    'urls': [],
                    'url_blacklist': []
                }
            }, is_black_url,

        # urlが存在すればblacklistのurlかどうかをチェック
        urls_blacklist = []
        for url in urls:
            if self._filter_url(url):
                continue
            res_find = self._find_url(url)
            if res_find:
                urls_blacklist.append(res_find)

            for black_url in app.config['BLACKLIST_URLS']:
                if black_url in url:
                    is_black_url = True

            # urlがgoo.glであれば実際のurlを抜き出し、指定されたurlと合致するかをチェック
            if 'goo.gl' in url:
                real_url = self._extract_href_short_google(url)
                for black_url in app.config['BLACKLIST_URLS']:
                    if black_url in real_url:
                        urls_blacklist.append(real_url)
                        is_black_url = True

        return {
            'url': {
                'urls': urls,
                'url_blacklist': urls_blacklist
            }
        }, is_black_url,
