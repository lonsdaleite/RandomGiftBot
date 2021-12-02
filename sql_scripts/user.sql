create table if not exists user (
    user_id int,
    tg_id int,
    notification_time varchar,
    min_days_num int,
    max_days_num int,
    deleted_flg char(1),
    processed_dttm timestamp
);
