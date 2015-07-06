from db import *

class GlobalConfig(object):
    def __init__(self,conf,log,db):
        self.conf=conf
        self.log=log
        self.db=db


    def update(self,cfg):
        cfg_map=self.db.find_one(DB.GLOBAL_CONFIG_TABLE,None)
        if not cfg_map:
            self.db.insert(DB.GLOBAL_CONFIG_TABLE,cfg)
        else:
            self.db.update(DB.GLOBAL_CONFIG_TABLE,{},cfg)

    @property
    def main_page(self):
        cfg_map=self.db.find_one(DB.GLOBAL_CONFIG_TABLE,None)
        if not cfg_map:
            return ""

        return self.db.find_one(DB.GLOBAL_CONFIG_TABLE,None).get(DB.MAIN_PAGE_KEY,"")
