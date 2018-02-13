/**
 *  Example
 *  create database {your_database_name};
 *  mysql -h 127.0.0.1 --port 3306 -u {your_name} {your_database_name} < create_table_urls.sql
 *  show create table urls;
 *
 */

CREATE TABLE `urls` (
   `id`                INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   `datetime`          DATETIME NOT NULL    COMMENT 'Datetime crawled',
   `pwa`               TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0: False, 1: True Progressive Web Appページかどうか',
   `scheme`            TINYINT(1) NOT NULL    COMMENT '0: http, 1: https',
   `netloc`            VARCHAR(255) NOT NULL  COMMENT 'net location',
   `path`              VARCHAR(255) NOT NULL  COMMENT 'path',
   `urls_external`     TEXT COMMENT 'JSON Type. External urls crawled page have.'
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8;

create index datetime_index on urls(datetime);
create index netloc_index on urls(netloc);
