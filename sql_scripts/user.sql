create table if not exists user (
    user_id int,
    tg_id int,
    notification_time varchar,
    min_days_num int,
    max_days_num int,
    processed_dttm timestamp
);