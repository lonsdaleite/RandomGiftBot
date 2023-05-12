-- ALTER TABLE notification_log RENAME TO notification_log_bckp20230512;

create table if not exists notification_log (
    user_id int not null,
    time_zone int not null,
    notification_time varchar not null,
    sent_flg char(1) not null,
    is_active_flg char(1) not null,
    processed_dttm timestamp not null
);

--INSERT INTO notification_log
--SELECT
--    user_id,
--    3 AS time_zone,
--    notification_time,
--    sent_flg,
--    is_active_flg,
--    processed_dttm
--FROM notification_log_bckp20230512
--;
