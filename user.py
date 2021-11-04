from db import select_actions
from db import dml_actions

class User:
    def __init__(self, user_id, tg_id):
        self.user_id = None
        self.tg_id = None
        self.notification_time = None
        self.min_days_num = None
        self.max_days_num = None
        
        self.update_args(user_id, tg_id)

    def check(self):
        if     self.tg_id is None \
            or self.notification_time is None \
            or self.min_days_num is None \
            or self.max_days_num is None :
            return False
        return True

    def update_args(self, user_id, tg_id):
        user_info = select_actions.get_user_info(user_id, tg_id)

        if user_info is not None:
            self.user_id = user_info["user_id"]
            self.tg_id = user_info["tg_id"]
            self.notification_time = user_info["notification_time"]
            self.min_days_num = user_info["min_days_num"]
            self.max_days_num = user_info["max_days_num"]
            
    def update(self):
        self.update_args(self.user_id, self.tg_id)

    