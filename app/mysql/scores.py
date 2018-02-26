# coding: utf-8

from app import app
from app.mysql.connect import Connect


class Scores():
    '''
    This class is need to be called with context manager
    e.g.
    with Urls() as u:
        is_exist = tu.is_exist('https://www.example.com')
    if is_exist:
        pass
    '''

    def __init__(self, role='master'):
        self.role = role

    def __enter__(self):
        self.con = Connect(role=self.role)
        self.m = self.con.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        '''
        意図的にcloseしないとすぐこのエラーが発生する。
        ReferenceError: weakly-referenced object no longer exists
        '''
        if exc_type is None:
            self.con.close()
        else:
            app.logger.warning('Urls mysql connection closing is failed')
            return False

    def add(self, urls):
        '''
        :param tuple urls
        :return int ID was inserted
        '''

        query = ('''
            INSERT INTO scores (
                created_at,
                updated_at,
                url_id,
                ssl,
                performance,
                pwa,
                accessibility,
                best_practice,
                seo
            ) VALUES (
                NOW(), NOW(), %s, %s, %s, %s, %s, %s, %s)
        ''')

        params = (
            urls['url_id'],
            urls['ssl'],
            urls['performance'],
            urls['pwa'],
            urls['accessibility'],
            urls['best_practice'],
            urls['seo'])

        self.m.execute(query, params)
        self.con.commit()
        return self.m.lastrowid

    def is_exist(self, url_id):
        '''
        存在しなければ0, 存在すれば1を返す
        :param int url_id
        :return int
        '''
        query = '''
            SELECT
            Score.id
            FROM scores AS Score
            WHERE
            Score.url_id = %s
        '''

        self.m.execute(query, (url_id,))
        return self.m.rowcount
