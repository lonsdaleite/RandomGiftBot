create table if not exists gift (
    user_id int,
    gift_dt date,
    done_flg char(1),
    is_active_flg char(1),
    processed_dttm timestamp
);
