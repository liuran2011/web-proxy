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

    def _proxy_in_request(self,uri_prefix,request):
        for req in request:
            if req['uriPrefix']==uri_prefix:
                return True
        
        return False

    def _sanity_check_proxy(self,request):
        for uri_prefix,port in self.ngix_mgr():
            if not self._proxy_in_request(uri_prefix,request):
                self.log.info("uri_prefix:%s port:%d not in add proxy config request. del it."
                             %(uri_prefix,port))
                self.ngix_mgr.del_proxy(uri_prefix)

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

            if public_url:
                item['result']="ok"
                item['publicURL']=public_url
            
            result.append(copy.deepcopy(item))
   
        self._sanity_check_proxy(request.json)

        return jsonify({"url":result}),200

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
