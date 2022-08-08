create table if not exists gift (
    user_id int not null,
    gift_dt date not null,
    is_active_flg char(1) not null,
    processed_dttm timestamp not null
);
