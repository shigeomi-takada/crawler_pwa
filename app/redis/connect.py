# coding: utf-8

import os
import sys
import redis
import fakeredis


class Connect():
    '''
    Redisとの接続に関する処理
    '''

    def __init__(self, host='api', role='master', decode_responses=True):
        '''
        @param str host
            You can set 'api' or 'pubsub'
            default is 'api'

        @param str role
            default is 'master'

        @param bool decode_responses
        '''
        self.role = role
        self.host = host
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
            self.r = fakeredis.FakeStrictRedis(
                decode_responses=True,
                charset="utf-8"
            )

            return self.r

        else:

            if self.host == 'pubsub':
                # Connect to PUBSUB master
                host = os.getenv('REDIS_PUBSUB_MASTER_HOSTNAME')
                password = os.getenv('REDIS_PUBSUB_MASTER_PASSWORD')
                port = os.getenv('REDIS_PUBSUB_MASTER_PORT', 6379)
                db = os.getenv('REDIS_PUBSUB_MASTER_DB', 0)
            else:
                if self.role == 'slave':
                    host = os.getenv('REDIS_API_SLAVE_HOSTNAME')
                    password = os.getenv('REDIS_API_SLAVE_PASSWORD')
                    port = os.getenv('REDIS_API_SLAVE_PORT', 6379)
                    db = os.getenv('REDIS_API_SLAVE_DB', 0)
                else:
                    host = os.getenv('REDIS_API_MASTER_HOSTNAME')
                    password = os.getenv('REDIS_API_MASTER_PASSWORD')
                    port = os.getenv('REDIS_API_MASTER_PORT', 6379)
                    db = os.getenv('REDIS_API_MASTER_DB', 0)

            self.r = redis.StrictRedis(
                host=host,
                password=password,
                port=port,
                db=db,
                decode_responses=self.decode_responses,
                socket_timeout=60
            )

            return self.r

    def is_connect(self):
        '''
        Check Redis Connection
        @return bool
        '''

        r = self.open()

        try:
            # 正常であればTrueが返る
            ping = r.ping()

            if ping:
                return True

        except:
            return False
