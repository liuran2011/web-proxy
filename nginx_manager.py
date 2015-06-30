import os
from constants import *
from port_mgr import PortMgr

class NginxManager(object):
    def __init__(self,conf,log):
        self.conf=conf
        self.log=log

        self.port_mgr=PortMgr(self.log,self.conf)

        self._load_proxy_config()
   
    def _parse_config(self,path,file):
        uri_prefix=None
        port=None

        for line in open("/".join(path,file),"r"):
            line=line.strip().rstrip()
            if line.startswith("server_name"):
                key,value=line.split()
                uri_prefix=value.rstrip(";")
            elif line.startswith("listen"):
                key,value=line,split()
                port=value.rstrip(";")
        
        if uri_prefix and port:
            self.port_mgr.map_port(uri_prefix,port)
            
    def _load_proxy_config(self):
        #TODO load proxy config from disk
        path=self.conf.nginx_config_path+"/sites-enabled"
        
        for entry in os.listdir(path):
            if entry=="default" or entry.startswith("."):
                continue
            
            self._parse_config(path,entry)

    def _reload(self):
        os.system("nginx -s reload")

    def _nginx_log_level(self):
        levels={'debug':'debug',
                'info':'info',
                'warning':'notice',
                'error':'error',
                'critical':'crit'}
        return levels.get(self.conf.log_level,'notice')

    def add_proxy(self,uri_prefix,proxy_uri):
        if self.port_mgr.port_exist(uri_prefix):
            return

        port=self.port_mgr.alloc_port(uri_prefix)
        if not port:
            self.log.error("uri_preifx: %s add proxy failed. port not avail."%(uri_prefix))
            return

        config_file=self.conf.nginx_config_path+"/sites-enabled/"+uri_prefix

        with open(config_file,"w") as f:
            config=NGINX_WEB_PROXY_FILE_TEMPLATE%(port,
                                                  self.conf.log_path+"/"+uri_prefix+'_proxy.log',
                                                  self._nginx_log_level(),
                                                  uri_prefix,
                                                  proxy_uri)
            f.write(config)
            f.close()

        self._reload()

    def del_proxy(self,uri_prefix):
        path=self.conf.nginx_config_path+"/sites-enabled/"+uri_prefix
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(path)

        self.port_mgr.free_port(uri_prefix)

        self._reload()
