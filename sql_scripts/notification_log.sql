create table if not exists notification_log (
    user_id int not null,
    notification_time varchar not null,
    sent_flg char(1) not null,
    is_active_flg char(1) not null,
    processed_dttm timestamp not null
);
