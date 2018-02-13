# coding: utf-8

import os
import sys
import mysql.connector
from flask import abort


class Connect():
    '''
    MYSQL Connection
    '''

    def __init__(self, role='master'):
        '''
        :param str role
            You can set 'master' or 'slave'
            Default is 'master'
        '''
        self.role = role

    def open(self):
        ''''''
        # テストの時はmasterに接続する
        if sys.argv[0] == 'python -m unittest':
            mysql_config = {
                'user': os.getenv('MYSQL_MASTER_USER'),
                'password': os.getenv('MYSQL_MASTER_PASSWORD'),
                'host': os.getenv('MYSQL_MASTER_HOSTNAME'),
                'port': os.getenv('MYSQL_MASTER_PORT'),
                'database': os.getenv('MYSQL_MASTER_DATABASE'),
                'buffered': True,
            }
        elif self.role == 'slave':
            mysql_config = {
                'user': os.getenv('MYSQL_READ_USER'),
                'password': os.getenv('MYSQL_READ_PASSWORD'),
                'host': os.getenv('MYSQL_READ_HOSTNAME'),
                'port': os.getenv('MYSQL_READ_PORT'),
                'database': os.getenv('MYSQL_READ_DATABASE'),
                'buffered': True,
                # 時間のかかるSQLもこのtimeoutの対象になるので、設定しなくてよい
                # 'connection_timeout': 3
            }
        else:
            mysql_config = {
                'user': os.getenv('MYSQL_MASTER_USER'),
                'password': os.getenv('MYSQL_MASTER_PASSWORD'),
                'host': os.getenv('MYSQL_MASTER_HOSTNAME'),
                'port': os.getenv('MYSQL_MASTER_PORT'),
                'database': os.getenv('MYSQL_MASTER_DATABASE'),
                'buffered': True,
            }

        try:
            # connectに直接configの中身を渡すとエラーになる。
            # mysqlはredisと違ってこの時点で接続できる否かを判別する
            self.cnx = mysql.connector.connect(**mysql_config)
        except Exception as e:
            abort(500, 'Error connecting to MySQL timed out')

        # dictionaryをTrueにすると返り値を辞書形式にする。何も指定しなければタプルになる
        self.cursor = self.cnx.cursor(dictionary=True)
        return self.cursor

    def commit(self):
        '''
        insert, update, deleteした時はクエリーの実行結果をDBに反映させるためにcommitを
        実行する必要がある。selectの時は必要ない。
        '''
        return self.cnx.commit()

    def close(self):
        '''
        Close MYSQL Connection
        '''
        self.cursor.close()
        self.cnx.close()

    def is_connect(self):
        '''
        Check MYSQL Connection
        :return bool
        '''
        self.open()
        return self.cnx.is_connected()
