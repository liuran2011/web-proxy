import os
from constants import *
from port_mgr import PortMgr
from utils import URL

class NginxManager(object):

    WEB_PROXY_PREFIX="nfcloud_si_"

    def __init__(self,conf,log,db,global_cfg,proxy_mgr):
        self.conf=conf
        self.log=log
        self.db=db
        self.global_cfg=global_cfg
        self.proxy_mgr=proxy_mgr

        self.port_mgr=PortMgr(self.log,self.conf,self.db)

        self._load_proxy_config()

    def _load_proxy_config(self):
        path=self.conf.nginx_config_path+"/conf.d"
        
        for entry in os.listdir(path):
            if not entry.startswith(NginxManager.WEB_PROXY_PREFIX):
                continue
            
            os.remove('/'.join([path,entry]))
        
        for uri_prefix,web_url,port in self.proxy_mgr.list_proxy():
            self._add_proxy_nginx(uri_prefix,web_url,port)
        
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

    def _public_url(self,port,path):
        url="http://"+self.conf.proxy_public_address+":"+str(port)+path

        return url

    def add_proxy(self,uri_prefix,proxy_uri):
        port,web_url=self.proxy_mgr.find_proxy(uri_prefix)
        if port:
            if proxy_uri==web_url:
                print web_url
                return self._public_url(port,URL.get_path(web_url));
            else:
                self.log.info("uri_prefix %s web_url change from %s to %s"
                              %(uri_prefix,web_url,proxy_uri))
                self.del_proxy(uri_prefix)

        port=self.port_mgr.alloc_port()
        if not port:
            self.log.error("uri_preifx: %s add proxy failed. port not avail."%(uri_prefix))
            return None

        self.proxy_mgr.add_proxy(uri_prefix,proxy_uri,port)

        self._add_proxy_nginx(uri_prefix,proxy_uri,port)

        self._reload()
       
        print proxy_uri

        return self._public_url(port,URL.get_path(proxy_uri))

    def _add_proxy_nginx(self,uri_prefix,proxy_uri,port):
        self.log.info("nginx add proxy uri_prefix:%s port:%d"%(uri_prefix,port))

        config_file=self.conf.nginx_config_path+"/conf.d/"+uri_prefix+".conf"

        with open(config_file,"w") as f:
            config=NGINX_WEB_PROXY_FILE_TEMPLATE%(port,
                                                  self.conf.log_path+"/"+uri_prefix+'_proxy.log',
                                                  self._nginx_log_level(),
                                                  os.getcwd()+'/static',
                                                  self.conf.rest_server_address,
                                                  self.conf.rest_server_port,
                                                  URL.get_base(proxy_uri),
                                                  self.conf.rest_server_address,
                                                  self.conf.rest_server_port
                                                  )
            f.write(config)
            f.close()

    def _del_proxy_nginx(self,uri_prefix):
        path=self.conf.nginx_config_path+"/conf.d/"+uri_prefix+".conf"
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(path)
      
    def del_proxy(self,uri_prefix):
        self.log.info("nginx del proxy uri_prefix:%s"%(uri_prefix))
        
        self._del_proxy_nginx(uri_prefix)

        path=self.conf.log_path+"/"+uri_prefix+"_proxy.log"
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(path)

        port,web_url=self.proxy_mgr.find_proxy(uri_prefix)
        if port:
            self.port_mgr.free_port(int(port))
       
        self.proxy_mgr.del_proxy(uri_prefix)

        self._reload()
