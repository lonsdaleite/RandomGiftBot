create table if not exists user (
    user_id int not null,
    tg_id int not null,
    notification_time varchar,
    min_days_num int,
    max_days_num int,
    time_to_gift_flg char(1) not null,
    deleted_flg char(1) not null,
    processed_dttm timestamp not null
);
