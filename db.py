import pymongo
import sys

class DB(object):
    DB_NAME="web_proxy"

    TOKEN_TABLE="token"
    USER_TABLE="user"
    PROXY_TABLE="proxy"
    PORT_TABLE="port"
    GLOBAL_CONFIG_TABLE="global_config"

    USER_NAME_KEY="userName"
    URI_PREFIX_KEY="uriPrefix"
    WEB_URL_KEY="webURL"
    TOKEN_KEY="token"
    MD5_KEY="md5"
    PORT_KEY="port"
    PORT_LIST_KEY="port_list"
    MAIN_PAGE_KEY="main_page"
    GLOBAL_CONF_KEY="global_config"

    def __init__(self,conf,log):
        self.conf=conf
        self.log=log
       
        self._init_mongodb()

    def _init_mongodb(self):
        while True:
            try:    
                self.connect=pymongo.mongo_client.MongoClient(
                                        self.conf.mongodb_address,
                                        self.conf.mongodb_port)
                self.db=self.connect.__getattr__(DB.DB_NAME)
                break
            except pymongo.errors.ConnectionFailure as e:
                self.log.error("connect to mongo db %s:%d failed. retry..."%(
                    self.conf.mongodb_address,self.conf.mongodb_port))
                continue
            
    def find_one(self,table,key):
        return self.db.__getattr__(table).find_one(key)
    
    def insert(self,table,value):
        self.db.__getattr__(table).insert(value)

    def update(self,table,key,value):
        self.db.__getattr__(table).update(key,value)

    def remove(self,table,key):
        self.db.__getattr__(table).remove(key) 
    
    def find(self,table,key):
        return self.db.__getattr__(table).find(key)

    def find_limit(self,table,key,col):
        return self.db.__getattr__(table).find(key,col)

    def add_to_set(self,table,key,set_name,value):
        return self.db.__getattr__(table).update(key,{"$addToSet":{set_name:value}})

    def add_to_set_multi(self,table,key,set_name,value_list):
        return self.db.__getattr__(table).update(key,{"$addToSet":{set_name:{"$each":value_list}}})

    def pull(self,table,key,set_name,value):
        return self.db.__getattr__(table).update(key,{"$pull":{set_name:value}})
