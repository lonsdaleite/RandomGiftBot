create table if not exists notification_log (
    user_id int,
    notification_time varchar,
    is_active_flg char(1),
    processed_dttm timestamp
);
