from flask import *
import copy

class RestServer(object):
    def __init__(self,conf,nginx_mgr,log):
        self.conf=conf
        self.log=log
        self.nginx_mgr=nginx_mgr

        self.app=Flask(__name__)
        self.app.add_url_rule(self.conf.url_prefix+'/',
                             'add_proxy_config',
                             self._add_proxy_config,
                             methods=['POST']) 
        self.app.add_url_rule(self.conf.url_prefix+'/<string:uri_prefix>',
                            'del_proxy_config',
                            self._del_proxy_config,
                            methods=['DELETE'])

    def _add_proxy_config(self):
        self.log.debug("add_proxy_config %s"%request.json)

        if not request.json:
            return jsonify({"error":"Bad Request"}),400

        result=[]
        for entry in request.json: 
            public_url=self.nginx_mgr.add_proxy(entry['uriPrefix'],
                                                entry['webUrl'])

            item={'uriPrefix':entry['uriPrefix'],
                  'result':'error',
                  'publicURL':None}

            if not public_url:
                item['result']="ok"
                item['publicURL']=public_url
            
            result.append(copy.deepcopy(item))

        return jsonify([result]),200

    def _del_proxy_config(self,uri_prefix):
        self.log.debug("del_proxy_config uri_prefix %s"%uri_prefix)
        
        self.nginx_mgr.del_proxy(uri_prefix)

        return jsonify({'result':'ok'}),200

    def run_server(self):
        self.log.info('rest server run at %s:%d%s'%(self.conf.rest_server_address,
                                                  self.conf.rest_server_port,
                                                  self.conf.url_prefix))

        self.app.run(self.conf.rest_server_address,
                     self.conf.rest_server_port,
                     True)
