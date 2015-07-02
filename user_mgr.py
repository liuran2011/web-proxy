from db import DB

class UserMgr(object):
    def __init__(self,conf,log,db):
        self.conf=conf
        self.log=log
        self.db=db

    def collect_user(self):
        user_map=self.db.find_limit(DB.USER_TABLE,{DB.USER_NAME:1})
        return set(map(lambda x:x[DB.USER_NAME_KEY],user_map))

    def add_user(self,user,uri_prefix):
        user_map=self.db.find_one(DB.USER_TABLE,{DB.USER_NAME_KEY,user})
        if not user_map:
            user_map={DB.USER_NAME_KEY:user,DB.URI_PREFIX_KEY:[uri_prefix]}
            self.db.insert(user_map)
        else:
            if uri_prefix not in user_map[DB.URI_PREFIX_KEY]:
                user_map[DB.URI_PREFIX_KEY].append(uri_prefix)
                self.db.update(DB.USER_TABLE,{DB.USER_NAME_KEY:user},user_map)

    def del_user(self,user):
        self.db.remove(DB.USER_TABLE,{DB.USER_NAME_KEY:user})
