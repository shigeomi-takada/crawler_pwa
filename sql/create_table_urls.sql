/**
 *  Example
 *  create database {your_database_name};
 *  mysql -h 127.0.0.1 --port 3306 -u {your_name} {your_database_name} < create_table_urls.sql
 *  show create table urls;
 *
 */

CREATE TABLE `urls` (
   `id`                INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   `created_at`        DATETIME NOT NULL      COMMENT 'Datetime crawled',
   `pwa`               TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0: Not PWA, 1: PWA',
   `scheme`            TINYINT(1) NOT NULL    COMMENT '0: http, 1: https',
   `netloc`            VARCHAR(255) NOT NULL  COMMENT 'FQDN: www.exmple.com',
   `host`              VARCHAR(255) NOT NULL  COMMENT 'www.exmple.comのwww部分',
   `domain`            VARCHAR(255) NOT NULL  COMMENT 'www.exmple.comのexmple.com部分',
   `path`              VARCHAR(255) NOT NULL  COMMENT 'path',
   `urls_external`     TEXT COMMENT 'JSON Type. External urls crawled page have.'
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8;

create index created_at_index on urls(created_at);
create index netloc_index on urls(netloc);
create index host_index on urls(host);
create index domain_index on urls(domain);
create index path_index on urls(path);
