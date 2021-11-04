create table if not exists gift (
    user_id int,
    gift_dt date,
    is_active_flg char(1),
    processed_dttm timestamp
);
