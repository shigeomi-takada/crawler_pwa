# coding: utf-8

import os
import sys
import redis
import fakeredis

from app import app


class Connect():
    '''
    Redisとの接続に関する処理
    '''

    def __init__(self, role='master', decode_responses=True):
        '''
        @param str role
            You can set 'master' or 'slave'
            Default is 'master'
        '''
        self.role = role
        self.decode_responses = decode_responses

    def open(self):
        '''
        decode_responsesをtrueにしないと、返り値がbyte型になる　
        例: [(b'1489238', 0.055784604491181125)]
        trueにしない場合は自分でByte型になっている箇所を文字列として扱うためにデコードする必要がある
        このタイミングではRedisとの接続チェックは行われない。コマンドを実行した時点でredisとの
        接続が発生する。
        '''

        # テストの時はfakeredisに接続する
        if sys.argv[0] == 'python -m unittest':
            return fakeredis.FakeStrictRedis(
                decode_responses=True,
                charset="utf-8")

        if self.role == 'slave':
            host = os.getenv('REDIS_SLAVE_HOSTNAME')
            password = os.getenv('REDIS_SLAVE_PASSWORD')
            port = os.getenv('REDIS_SLAVE_PORT', 6379)
            db = os.getenv('REDIS_SLAVE_DB')

            # decode_responses == Falseの時はキャッシュしない
            if self.decode_responses == False:
                return redis.StrictRedis(
                    host=host,
                    password=password,
                    port=port,
                    db=db,
                    decode_responses=self.decode_responses,
                    socket_timeout=60)

            # redisはデフォルトでコネクションプールが張られる
            if ('REDIS_CON_SLAVE' in app.config and
                app.config['REDIS_CON_SLAVE']):
                return app.config['REDIS_CON_SLAVE']
            else:
                app.config['REDIS_CON_SLAVE'] = redis.StrictRedis(
                    host=host,
                    password=password,
                    port=port,
                    db=db,
                    decode_responses=self.decode_responses,
                    socket_timeout=60)
                return app.config['REDIS_CON_SLAVE']

        elif self.role == 'master':
            host = os.getenv('REDIS_MASTER_HOSTNAME')
            password = os.getenv('REDIS_MASTER_PASSWORD')
            port = os.getenv('REDIS_MASTER_PORT', 6379)
            db = os.getenv('REDIS_MASTER_DB')
            # redisはデフォルトでコネクションプールが張られる
            if ('REDIS_CON_MASTER' in app.config and
                app.config['REDIS_CON_MASTER']):
                return app.config['REDIS_CON_MASTER']
            else:
                app.config['REDIS_CON_MASTER'] = redis.StrictRedis(
                    host=host,
                    password=password,
                    port=port,
                    db=db,
                    decode_responses=self.decode_responses,
                    socket_timeout=60)
                return app.config['REDIS_CON_MASTER']

        else:
            raise Exception('Invalid Args: redis role is wrong. \
                only master and slave')

    def is_connect(self):
        '''
        Check Redis Connection
        @return bool
        '''
        try:
            r = self.open()
            # 正常であればTrueが返る
            return r.ping()
        except:
            return False
