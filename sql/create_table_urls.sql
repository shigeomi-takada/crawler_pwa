

CREATE TABLE `scores` (
   `id`               INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
   `created_at`       DATETIME NOT NULL      COMMENT 'Datetime created',
   `updated_at`       DATETIME NOT NULL      COMMENT 'Datetime updated',
   `url_id`           INT UNSIGNED NOT NULL  COMMENT 'urls table id',
   `ssl`              TINYINT(1) NOT NULL    COMMENT 'sslに対応しているか否か',
   `performance`      FLOAT NOT NULL         COMMENT 'score',
   `pwa`              FLOAT NOT NULL         COMMENT 'score',
   `accessibility`    FLOAT NOT NULL         COMMENT 'score',
   `best_practice`    FLOAT NOT NULL         COMMENT 'score',
   `seo`              FLOAT NOT NULL         COMMENT 'score'
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8;

create index url_id_index on scores(url_id);
create index pwa_index on scores(pwa);
