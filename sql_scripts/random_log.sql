create table if not exists random_log (
    user_id int not null,
    since_latest_gift_days_cnt int not null,
    random_days_cnt int,
    is_active_flg char(1) not null,
    processed_dttm timestamp not null
);
