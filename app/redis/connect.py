# coding: utf-8

import os
import sys
import redis
import fakeredis


class Connect():
    '''
    Redis Connection
    '''

    def __init__(self, role='master', decode_responses=True):
        '''
        :param str role
            default is 'master'
        :param bool decode_responses
        '''
        self.role = role
        self.decode_responses = decode_responses

    def open(self):
        '''
        :return redis connection object
        '''
        # When test, connect to fakeredis
        if sys.argv[0] == 'python -m unittest':
            self.r = fakeredis.FakeStrictRedis(
                decode_responses=True,
                charset="utf-8")

            return self.r
        else:
            if self.role == 'slave':
                host = os.getenv('REDIS_SLAVE_HOSTNAME')
                password = os.getenv('REDIS_SLAVE_PASSWORD')
                port = os.getenv('REDIS_SLAVE_PORT', 6379)
                db = os.getenv('REDIS_SLAVE_DB', 0)
            else:
                host = os.getenv('REDIS_MASTER_HOSTNAME')
                password = os.getenv('REDIS_MASTER_PASSWORD')
                port = os.getenv('REDIS_MASTER_PORT', 6379)
                db = os.getenv('REDIS_MASTER_DB', 0)

            self.r = redis.StrictRedis(
                host=host,
                password=password,
                port=port,
                db=db,
                decode_responses=self.decode_responses,
                socket_timeout=60)

            return self.r

    def is_connect(self):
        '''
        Check Redis Connection
        :return bool
        '''
        try:
            if self.open().ping():
                return True
        except:
            return False
