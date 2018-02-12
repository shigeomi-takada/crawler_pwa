/**
 *  ファイルからテーブルを作成する
 *  create database siegel;
 *  mysql -h 127.0.0.1 --port 3306 -u root siegel < create_table_urls.sql
 *  show columns from <テーブル名>
 *
 */

CREATE TABLE `urls` (
   `id`                INT(11) PRIMARY KEY AUTO_INCREMENT,
   `datetime`          DATETIME NOT NULL    COMMENT 'クローリングした時間',
   `scheme`            TINYINT(1) NOT NULL    COMMENT '0: http, 1: https',
   `netloc`            VARCHAR(255) NOT NULL  COMMENT 'net location',
   `path`              VARCHAR(255) NOT NULL  COMMENT 'path part',
   `pwa`               TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0: False, 1: True Progressive Web Appページかどうか',
   `urls_external`     TEXT COMMENT 'JSON ページが持っている外部リンク'
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8;

create index datetime_index on urls(datetime);
create index netloc_index on urls(netloc);
