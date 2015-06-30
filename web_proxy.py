#!/usr/bin/env python

import gevent.monkey
gevent.monkey.patch_all()

#from contrail import contrail_veth_port
from conf import Config
from nginx_manager import NginxManager
from rest_server import RestServer
from log import Logger
import os

class WebProxy(object):
    def __init__(self):
        self.conf=Config()
        self._prepare()
        self.log=Logger(self.conf)
        self.nginx_mgr=NginxManager(self.conf,self.log)
        self.rest_server=RestServer(self.conf,self.nginx_mgr,self.log)

    def _prepare(self):
        if not os.path.exists(self.conf.proxy_config_path):
            os.makedirs(self.conf.proxy_config_path)

        if not os.path.exists(self.conf.log_path):
            os.makedirs(self.conf.log_path)

    def main(self):
        self.rest_server.run()

if __name__=="__main__":
    server=WebProxy()
    server.main()    
