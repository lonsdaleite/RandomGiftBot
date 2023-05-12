-- ALTER TABLE user RENAME TO user_bckp20230512;

create table if not exists user (
    user_id int not null,
    tg_id int not null,
    time_zone int,
    notification_time varchar,
    min_days_num int,
    max_days_num int,
    time_to_gift_flg char(1) not null,
    deleted_flg char(1) not null,
    processed_dttm timestamp not null
);

--INSERT INTO user
--SELECT
--    user_id,
--    tg_id,
--    3 AS time_zone,
--    notification_time,
--    min_days_num,
--    max_days_num,
--    time_to_gift_flg,
--    deleted_flg,
--    processed_dttm
--FROM user_bckp20230512
--;
