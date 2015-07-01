import os
from constants import *
from port_mgr import PortMgr

class NginxManager(object):
    def __init__(self,conf,log):
        self.conf=conf
        self.log=log

        self.port_mgr=PortMgr(self.log,self.conf)

        self._load_proxy_config()
  
    def __iter__(self):
        self.port_mgr_iter=self.port_mgr.iteritems()
        return self.port_mgr_iter

    def __next__(self):
        return next(self.port_mgr_iter)

    def _parse_config(self,path,file):
        uri_prefix=None
        port=None

        for line in open("/".join([path,file]),"r"):
            line=line.strip().rstrip()
            if line.startswith("server_name"):
                key,value=line.split()
                uri_prefix=value.rstrip(";")
            elif line.startswith("listen"):
                key,value=line.split()
                port=value.rstrip(";")
        
        if uri_prefix and port:
            self.log.info("nginx proxy exist. uri_prefix:%s port:%s"%(uri_prefix,port))
            self.port_mgr.map_port(uri_prefix,int(port))
            
    def _load_proxy_config(self):
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

    def _public_url(self,port):
        return "http://"+self.conf.proxy_public_address+":"+str(port)

    def add_proxy(self,uri_prefix,proxy_uri):
        port=self.port_mgr.find_port(uri_prefix)
        if port:
            return self._public_url(port)

        port=self.port_mgr.alloc_port(uri_prefix)
        if not port:
            self.log.error("uri_preifx: %s add proxy failed. port not avail."%(uri_prefix))
            return None

        self.log.info("nginx add proxy uri_prefix:%s port:%d"%(uri_prefix,port))

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

        return self._public_url(port)

    def del_proxy(self,uri_prefix):
        path=self.conf.nginx_config_path+"/sites-enabled/"+uri_prefix
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(path)

        self.log.info("nginx del proxy uri_prefix:%s"%(uri_prefix))

        self.port_mgr.free_port(uri_prefix)

        self._reload()
