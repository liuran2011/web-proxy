from flask import *

class RestServer(object):
    def __init__(self,conf,nginx_mgr,log):
        self.conf=conf
        self.log=log
        self.nginx_mgr=nginx_mgr

        self.app=Flask(__name__)
        self.app.add_url_rule(self.conf.url_prefix+'/config',
                             'add_proxy_config',
                             self.add_proxy_config,
                             methods=['POST']) 
        self.app.add_url_rule(self.conf.url_prefix+'/config/<string:uri_prefix>',
                            'del_proxy_config',
                            self.del_proxy_config,
                            methods=['DELETE'])

    def add_proxy_config(self):
        self.log.debug("add_proxy_config %s"%request.json)

        self.nginx_mgr.add_proxy(request.json)
        return jsonify({'ok':'ok'}),201

    def del_proxy_config(self,uri_prefix):
        self.log.debug("del_proxy_config uri_prefix %s"%uri_prefix)

        return jsonify({'error':'error'}),200

    def run(self):
        self.app.run(self.host,self.port,True)
