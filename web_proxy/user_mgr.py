from db import DB

class UserMgr(object):
    def __init__(self,conf,log,db):
        self.conf=conf
        self.log=log
        self.db=db

    def collect_user(self):
        user_map=self.db.find_limit(DB.USER_TABLE,None,{DB.USER_NAME_KEY:1})
        return set(map(lambda x:x[DB.USER_NAME_KEY],user_map))

    def add_user(self,user,uri_prefix_list):
        user_map=self.db.find_one(DB.USER_TABLE,{DB.USER_NAME_KEY:user})
        if not user_map:
            user_map={DB.USER_NAME_KEY:user,DB.URI_PREFIX_KEY:uri_prefix_list}
            self.db.insert(DB.USER_TABLE,user_map)
            return

        self.db.add_to_set_multi(DB.USER_TABLE,
                                {DB.USER_NAME_KEY:user},
                                DB.URI_PREFIX_KEY,
                                uri_prefix_list)
    
    def del_user_uri_prefix(self,uri_prefix):
        user_map=self.db.find_one(DB.USER_TABLE,{DB.URI_PREFIX_KEY:uri_prefix})
        if not user_map:
            return

        user_map[DB.URI_PREFIX_KEY].remove(uri_prefix)

        if len(user_map[DB.URI_PREFIX_KEY])==0:
            self.del_user(user_map[DB.USER_NAME_KEY])
        else:
            self.db.pull(DB.USER_TABLE,
                    {DB.USER_NAME_KEY:user_map[DB.USER_NAME_KEY]},
                    DB.URI_PREFIX_KEY,uri_prefix)
           
    def del_user(self,user):
        self.db.remove(DB.USER_TABLE,{DB.USER_NAME_KEY:user})

    def user_has_uri_prefix(self,user,uri_prefix):
        user_map=self.db.find_one(DB.USER_TABLE,{DB.USER_NAME_KEY:user})
        if not user_map:
            return False

        if uri_prefix not in user_map[DB.URI_PREFIX_KEY]:
            return False

        return True 
