from db import DB

class PortMgr(object):
    def __init__(self,log,conf,db):
        self.conf=conf
        self.log=log
        self.db=db
        self.port_list=None

        self._port_list_init()

    def _port_list_init(self):
        self.port_list=self.db.find_one(DB.PORT_TABLE,None)
        if not self.port_list:
            self.log.info("port list table not exist, create it.")
            self.port_list={DB.PORT_LIST_KEY:[0 for x in range(self.conf.proxy_min_port,self.conf.proxy_max_port)]}
            self.db.insert(DB.PORT_TABLE,self.port_list)
           
        #TODO, check proxy_min_port and proxy_max_port if changed.

    def alloc_port(self):
        try:
            index=self.port_list[DB.PORT_LIST_KEY].index(0)
            self.port_list[DB.PORT_LIST_KEY][index]=1
            self.db.update(DB.PORT_TABLE,{},self.port_list)
            return index+self.conf.proxy_min_port
        except ValueError as e:
            self.log.error("port exausted.")
            return None

    def free_port(self,port):
        self.port_list[DB.PORT_LIST_KEY][port-self.conf.proxy_min_port]=0
        self.db.update(DB.PORT_TABLE,{},self.port_list)
