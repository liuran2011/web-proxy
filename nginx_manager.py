import os
from constants import *

class NginxManager(object):
    def __init__(self,conf,log):
        self.conf=conf
        self.log=log

        self._check_proxy_config()

    def _reload(self):
        os.system("nginx -s reload")

    def _nginx_log_level(self):
        levels={'debug':'debug',
                'info':'info',
                'warning':'notice',
                'error':'error',
                'critical':'crit'}
        return levels.get(self.conf.log_level,'notice')

    def _check_proxy_config(self):
        config_file=self.conf.nginx_config_path+"/sites-enabled/"+NGINX_WEB_PROXY_FILE_NAME
        if os.path.exists(config_file):
            return

        with open(config_file,"w") as f:
            config=NGINX_WEB_PROXY_FILE_TEMPLATE%(self.conf.proxy_port,
                                                  self.conf.log_path+'/nginx_proxy.log',
                                                  self._nginx_log_level(),
                                                  self.conf.proxy_config_path)
            f.write(config)
            f.close()
        
        self._reload()

    def add_proxy(self,uri_prefix,proxy_uri):
        config="""location %s {
                pass_proxy %s;
               }"""%(uri_prefix,proxy_uri)
        
        path=self.conf.proxy_config_path+"/"+uri_prefix

        with open(path,"w") as f:
            f.write(config)
            f.close()

        self._reload()

    def del_proxy(self,uri_prefix):
        path=self.conf.proxy_config_path+"/"+uri_prefix
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(path)

        self._reload()
