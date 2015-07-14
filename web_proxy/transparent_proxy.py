import urlparse

class TransparentProxyMgr(object):
    def __init__(self,conf,log,db):
        self.conf=conf
        self.db=db
        self.log=log

    def add_proxy(self,location):
        url_comps=urlparse.urlparse(location)
        net_locs=url_comps.netloc.split(':')
        port=TRANSPARENT_PROXY_DEFAULT_PORT
        
        if len(net_locs)>=2:
            self.log.info("location %s has no port, set port to %s"%(location,
                    TRANSPARENT_PROXY_DEFAULT_PORT))
            port=net_locs[1]

        if not self.db.find_one(DB.TRANS_PROXY_TABLE,{DB.LOCATION_KEY:location}):
            self.db.insert(DB.TRANS_PROXY_TABLE,{DB.LOCATION_KEY:location})

        return url_comps.scheme+"//"+self.conf.proxy_public_address+":"+str(port)

    def del_proxy(self,location):
        self.db.remove(DB.TRANS_PROXY_TABLE,{DB.LOCATION_KEY:location})

    def list_proxy(self):
        res=self.db.find(DB.TRANS_PROXY_TABLE,None)
        for node in res:
            yield node[DB.LOCATION_KEY]
