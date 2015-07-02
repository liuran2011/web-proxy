import os
from constants import *
from port_mgr import PortMgr
from db import DB

class NginxManager(object):
    def __init__(self,conf,log,db):
        self.conf=conf
        self.log=log
        self.db=db

        self.port_mgr=PortMgr(self.log,self.conf,self.db)

        self._load_proxy_config()

    def __iter__(self):
        return self.db.find_limit(DB.PROXY_TABLE,None,{DB.URI_PREFIX_KEY:1})

    def _load_proxy_config(self):
        path=self.conf.nginx_config_path+"/sites-enabled"
        
        for entry in os.listdir(path):
            if entry=="default" or entry.startswith("."):
                continue
            
            os.remove('/'.join([path,entry]))
        
        for entry in self.db.find(DB.PROXY_TABLE,None):
            self._add_proxy_nginx(entry[DB.URI_PREFIX_KEY],
                                  entry[DB.WEB_URL_KEY],
                                  entry[DB.PORT_KEY])
        
        self._reload()

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
        proxy_map=self.db.find_one(DB.PROXY_TABLE,{DB.URI_PREFIX_KEY,uri_prefix})
        if proxy_map:
            return self._public_url(proxy_map[DB.PORT_KEY]);

        port=self.port_mgr.alloc_port()
        if not port:
            self.log.error("uri_preifx: %s add proxy failed. port not avail."%(uri_prefix))
            return None

        self.log.info("nginx add proxy uri_prefix:%s port:%d"%(uri_prefix,port))
        self.db.update(DB.PROXY_TABLE,
                        {DB.URI_PREFIX_KEY:uri_prefix,
                        DB.WEB_URL_KEY:proxy_uri,
                        DB.PORT_KEY:port})
        public_url=self._add_proxy_nginx(uri_prefix,proxy_uri,port)

        self._reload()
        
        return public_url

    def _add_proxy_nginx(self,uri_prefix,proxy_uri,port):
        config_file=self.conf.nginx_config_path+"/sites-enabled/"+uri_prefix

        with open(config_file,"w") as f:
            config=NGINX_WEB_PROXY_FILE_TEMPLATE%(port,
                                                  self.conf.log_path+"/"+uri_prefix+'_proxy.log',
                                                  self._nginx_log_level(),
                                                  uri_prefix,
                                                  proxy_uri)
            f.write(config)
            f.close()

        return self._public_url(port)

    def _del_proxy_nginx(self,uri_prefix):
        path=self.conf.nginx_config_path+"/sites-enabled/"+uri_prefix
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(path)
      
    def del_proxy(self,uri_prefix):
        self.log.info("nginx del proxy uri_prefix:%s"%(uri_prefix))
        
        self._del_proxy_nginx(uri_prefix)

        path=self.conf.log_path+"/"+uri_prefix+"_proxy.log"
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(path)

        proxy_map=self.db.find_one(DB.PROXY_TABLE,{DB.URI_PREFIX_KEY:uri_prefix})
        if proxy_map:
            self.port_mgr.free_port(proxy_map[DB.PORT_KEY])
        
        self.db.remove(DB.PROXY_TABLE,{DB.URI_PREFIX_KEY:uri_prefix})

        self._reload()
