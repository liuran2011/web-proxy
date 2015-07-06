from db import DB
import hashlib

class TokenMgr(object):
    def __init__(self,conf,log,db):
        self.conf=conf
        self.log=log
        self.db=db

    def _md5(self,token):
        md5=hashlib.md5()
        md5.update(token)
        return md5.hexdigest()

    def add_token(self,user,token):
        token_map=self.db.find_one(DB.TOKEN_TABLE,{DB.USER_NAME_KEY:user})
        if not token_map:
            token_map={DB.USER_NAME_KEY:user,DB.TOKEN_KEY:token,DB.MD5_KEY:self._md5(token)}
            self.db.insert(DB.TOKEN_TABLE,token_map)
        
        if token != token_map[DB.TOKEN_KEY]:
            token_map[DB.TOKEN_KEY]=token
            token_map[DB.MD5_KEY]=self._md5(token)
            self.db.update(DB.TOKEN_TABLE,{DB.USER_NAME_KEY:user},token_map)

    def del_token(self,user):
        self.db.remove(DB.TOKEN_TABLE,{DB.USER_NAME_KEY:user})

    def find_token_from_md5(self,md5):
        return self.db.find_one(DB.TOKEN_TABLE,{DB.MD5_KEY:md5})[DB.TOKEN_KEY]
