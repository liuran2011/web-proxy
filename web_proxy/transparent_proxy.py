import urlparse
from db import DB

class TransparentProxyMgr(object):
    def __init__(self,conf,log,db):
        self.conf=conf
        self.db=db
        self.log=log

    def add_proxy(self,location,port):
        if not self.db.find_one(DB.TRANS_PROXY_TABLE,{DB.LOCATION_KEY:location}):
            self.db.insert(DB.TRANS_PROXY_TABLE,{DB.LOCATION_KEY:location,DB.PORT_KEY:port})

    def del_proxy(self,location):
        self.db.remove(DB.TRANS_PROXY_TABLE,{DB.LOCATION_KEY:location})

    def find_proxy(self,location):
        proxy_map=self.db.find_one(DB.TRANS_PROXY_TABLE,{DB.LOCATION_KEY:location})
        if not proxy_map:
            return None

        return proxy_map[DB.PORT_KEY]
        
    def list_proxy(self):
        res=self.db.find(DB.TRANS_PROXY_TABLE,None)
        for node in res:
            yield node[DB.LOCATION_KEY],node[DB.PORT_KEY]
