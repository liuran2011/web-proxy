from db import *

class ProxyMgr(object):
    def __init__(self,conf,log,db):
        self.conf=conf
        self.db=db
        self.log=log

    def find_proxy(self,uri_prefix):
        proxy_map=self.db.find_one(DB.PROXY_TABLE,{DB.URI_PREFIX_KEY:uri_prefix})
        if not proxy_map:
            return None,None

        return proxy_map[DB.PORT_KEY],proxy_map[DB.WEB_URL_KEY]

    def find_uri_prefix(self,port):
        proxy_map=self.db.find_one(DB.PROXY_TABLE,{DB.PORT_KEY:port})
        if not proxy_map:
            return None

        return proxy_map[DB.URI_PREFIX_KEY]

    def find_web_url(self,port):
        proxy_map=self.db.find_one(DB.PROXY_TABLE,{DB.PORT_KEY:port})
        if not proxy_map:
            return None

        return proxy_map[DB.WEB_URL_KEY]

    def add_proxy(self,uri_prefix,web_url,port):
        self.db.insert(DB.PROXY_TABLE,
                        {
                            DB.URI_PREFIX_KEY:uri_prefix,
                            DB.WEB_URL_KEY:web_url,
                            DB.PORT_KEY:port
                        }
                      )

    def del_proxy(self,uri_prefix):
        self.db.remove(DB.PROXY_TABLE,{DB.URI_PREFIX_KEY:uri_prefix})

    def list_proxy(self):
        res=self.db.find(DB.PROXY_TABLE,None)
        for node in res:
            yield node[DB.URI_PREFIX_KEY],node[DB.WEB_URL_KEY],node[DB.PORT_KEY]      


