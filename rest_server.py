from flask import *
import copy
from http_codes import *
from token_mgr import TokenMgr
from user_mgr import UserMgr

class RestServer(object):
    URI_PREFIX="uriPrefix"
    WEB_URL="webUrl"
    USER_NAME="userName"
    PUBLIC_URL="publicURL"
    RESULT="result"
    TOKEN="token"
    WEB_INFO="webInfo"

    def __init__(self,conf,nginx_mgr,log,db):
        self.conf=conf
        self.log=log
        self.nginx_mgr=nginx_mgr
        self.db=db
        self.token_mgr=TokenMgr(self.conf,self.log,self.db)
        self.user_mgr=UserMgr(self.conf,self.log,self.db)

        self.app=Flask(__name__)
        self.app.add_url_rule(self.conf.url_prefix+'/token',
                              'add_token',
                              self._add_token,
                              methods=['POST'])
        self.app.add_url_rule(self.conf.url_prefix+'/',
                             'add_proxy_config',
                             self._add_proxy_config,
                             methods=['POST']) 
        self.app.add_url_rule(self.conf.url_prefix+'/<string:uri_prefix>',
                            'del_proxy_config',
                            self._del_proxy_config,
                            methods=['DELETE'])

    def _sanity_check_proxy(self,request):
        proxy_del_list=[]
        
        req_uri_prefix_list=[]
        for user in request:
            req_uri_prefix_list+=map(lambda x:x[RestServer.URI_PREFIX],user[RestServer.WEB_INFO])

        for uri_prefix in self.nginx_mgr:
            if not uri_prefix in req_uri_prefix_list:
                self.log.info("uri_prefix:%s not in add proxy config request. del it."
                             %(uri_prefix))
                proxy_del_list.append(uri_prefix)

        for node in proxy_del_list:
            self.nginx_mgr.del_proxy(node)
   
    def _sanity_check_user(self,request):
        user_set=self.user_mgr.collect_user()
        req_user_set=set(map(lambda x: x[RestServer.USER_NAME],request))

        del_user_set=user_set-req_user_set
        for user in del_user_set:
            self.user_mgr.del_user(user)
            self.token_mgr.del_token(user)

    def _sanity_check(self,request):
        self._sanity_check_proxy(request)
        self._sanity_check_user(request)

    def _add_proxy_config_user(self,request):
        for req in request:
            self.user_mgr.add_user(req[RestServer.USER_NAME],
                                  map(lambda arg: arg[RestServer.URI_PREFIX],req[RestServer.WEB_INFO]))

    def _add_proxy_config(self):
        self.log.debug("add_proxy_config %s"%request.json)

        #request format
        #[{userName:test,webInfo:[{uriPrefix:xxx,webUrl:yyy}]}]
        if not request.json:
            return jsonify({"error":HTTP_BAD_REQUEST_STR}),HTTP_BAD_REQUEST
        
        self._add_proxy_config_user(request.json)
       
        result=self._add_proxy_config_nginx(request.json[RestServer.WEB_INFO])
        
        self._sanity_check(request.json)

        return result

    def _add_proxy_config_nginx(self,request):
        result=[]
        for entry in request: 
            public_url=self.nginx_mgr.add_proxy(entry[RestServer.URI_PREFIX],
                                                entry[RestServer.WEB_URL])

            item={RestServer.URI_PREFIX:entry[RestServer.URI_PREFIX],
                  RestServer.RESULT:'error',
                  RestServer.PUBLIC_URL:None}

            if public_url:
                item[RestServer.RESULT]="ok"
                item[RestServer.PUBLIC_URL]=public_url
            
            result.append(copy.deepcopy(item))

        return jsonify({"url":result}),HTTP_OK

    def _add_token(self):
        self.log.debug("add_token %s"%request.json)

        if not request.json:
            return jsonify({"error":HTTP_BAD_REQUEST_STR}),HTTP_BAD_REQUEST

        self.token_mgr.add_token(request.json[RestServer.USER_NAME],request.json[RestServer.TOKEN]) 

    def _del_proxy_config(self,uri_prefix):
        self.log.debug("del_proxy_config uri_prefix %s"%uri_prefix)
        
        self.nginx_mgr.del_proxy(uri_prefix)

        return jsonify({RestServer.RESULT:'ok'}),HTTP_OK

    def run_server(self):
        self.log.info('rest server run at %s:%d%s'%(self.conf.rest_server_address,
                                                  self.conf.rest_server_port,
                                                  self.conf.url_prefix))

        self.app.run(self.conf.rest_server_address,
                     self.conf.rest_server_port,
                     True)
