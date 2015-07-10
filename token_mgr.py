from db import DB
from utils import MD5

class TokenMgr(object):
    def __init__(self,conf,log,db):
        self.conf=conf
        self.log=log
        self.db=db

    def add_token(self,user,token):
        token_map=self.db.find_one(DB.TOKEN_TABLE,{DB.USER_NAME_KEY:user})
        if not token_map:
            token_map={DB.USER_NAME_KEY:user,DB.TOKEN_KEY:token,DB.MD5_KEY:MD5.get(token)}
            self.db.insert(DB.TOKEN_TABLE,token_map)
        
        if token != token_map[DB.TOKEN_KEY]:
            token_map[DB.TOKEN_KEY]=token
            token_map[DB.MD5_KEY]=MD5.get(token)
            self.db.update(DB.TOKEN_TABLE,{DB.USER_NAME_KEY:user},token_map)

    def del_token(self,user):
        self.db.remove(DB.TOKEN_TABLE,{DB.USER_NAME_KEY:user})

    def find_token_id(self,username):
        token_map=self.db.find_one(DB.TOKEN_TABLE,{DB.USER_NAME_KEY:username})
        if not token_map:
            return None

        return token_map.get(DB.MD5_KEY)

    def find_token(self,md5):
        token_map=self.db.find_one(DB.TOKEN_TABLE,{DB.MD5_KEY:md5})
        if not token_map:
            return None,None
            
        return token_map.get(DB.USER_NAME_KEY,None),token_map.get(DB.TOKEN_KEY,None)
