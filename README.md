# Crawler PWA


## Dependencies
- Python(>= 3.4)
- MYSQL
- Redis

## Installation

To download this repository, run:
```
git clone git@github.com:google/python-fire.git
```

To install Python packages, run:
```
pip install -r requirements.txt
```

To create .env file, run:
```
cp .env.example .env
```

And change at least the following setting with your environment's values.

```
# MYSQL MASTER
MYSQL_MASTER_HOSTNAME='127.0.0.1'
MYSQL_MASTER_PORT=3306
MYSQL_MASTER_USER=''
MYSQL_MASTER_PASSWORD=''
MYSQL_MASTER_DATABASE=''

# REDIS MASTER
REDIS_MASTER_HOSTNAME='127.0.0.1'
REDIS_MASTER_PORT=6379
REDIS_MASTER_PASSWORD=''
REDIS_MASTER_DB=0
```

To create `urls` table, run:
```
# if you need
mysql> create database {your_database_name};

cd crawler_pwa/sql
mysql -h {your_host} --port {your_port} -u {your_name} {your_database_name} < create_table_urls.sql
```

It's done.  
Let's use crawler_pwa.

## Basic Usage
**Before use crawler_pwa, you need to start Mysql and Redis.**

First, you need to set initial url to start crawling. run:

```python
python cpctl.py launch --url=https://www.python.org/
```

Some urls are pushed in redis.  
Key name is `cp:urls`.

We are ready to crawl.
To start crawling, run:
```python
python cpctl.py run
```

## Advanced Usage
You can use [supervisord](http://supervisord.org/) to run crawler_pwa.
```
supervisord -c supervisord.conf
```

## Disclaimer

This is not an official Lancers product.
