create table if not exists random_log (
    user_id int,
    since_latest_gift_days_cnt int,
    random_days_cnt int,
    is_active_flg char(1),
    processed_dttm timestamp
);
