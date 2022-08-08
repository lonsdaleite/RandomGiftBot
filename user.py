from db import select_actions
from db import dml_actions


class User:
    def __init__(self, user_id, tg_id):
        self.user_id = None
        self.tg_id = None
        self.notification_time = None
        self.min_days_num = None
        self.max_days_num = None
        self.latest_gift_dt = None
        self.time_to_gift_flg = None

        self.refresh_args(user_id, tg_id)

    def check(self):
        if self.tg_id is None \
                or self.notification_time is None \
                or self.min_days_num is None \
                or self.max_days_num is None \
                or self.latest_gift_dt is None:
            return False
        return True

    def refresh_args(self, user_id, tg_id):
        user_info = select_actions.get_user_info(user_id, tg_id)

        if user_info is not None:
            self.user_id = user_info["user_id"]
            self.tg_id = user_info["tg_id"]
            self.notification_time = user_info["notification_time"]
            self.min_days_num = user_info["min_days_num"]
            self.max_days_num = user_info["max_days_num"]
            self.time_to_gift_flg = True if user_info["time_to_gift_flg"] == "1" else False

        gift_info = select_actions.get_latest_gift(self.user_id)
        if gift_info is not None:
            self.latest_gift_dt = gift_info["gift_dt"]

    def refresh(self):
        self.refresh_args(self.user_id, self.tg_id)

    def add_gift(self, gift_dt):
        dml_actions.add_gift(self.user_id, gift_dt)
        self.refresh()

    def update_user_info(self, tg_id=None, notification_time=None, min_days_num=None, max_days_num=None,
                         time_to_gift_flg=None):
        dml_actions.update_user_info(self.user_id, tg_id=tg_id, notification_time=notification_time,
                                     min_days_num=min_days_num, max_days_num=max_days_num,
                                     time_to_gift_flg=time_to_gift_flg)
        self.refresh()
