from flask import *
import copy
from http_codes import *
from token_mgr import TokenMgr
from user_mgr import UserMgr
from global_config import GlobalConfig
from nginx_manager import NginxManager
from proxy_mgr import ProxyMgr
import re
from auth import Auth

class RestServer(object):
    URI_PREFIX="uriPrefix"
    WEB_URL="webUrl"
    USER_NAME="userName"
    PUBLIC_URL="publicURL"
    RESULT="result"
    ERROR="error"
    TOKEN="token"
    WEB_INFO="webInfo"
    MAIN_PAGE="mainPage"
    URL="url"

    def __init__(self,conf,log,db):
        self.conf=conf
        self.log=log
        self.db=db

        self.global_cfg=GlobalConfig(self.conf,self.log,self.db)
        self.proxy_mgr=ProxyMgr(self.conf,self.log,self.db)
        self.nginx_mgr=NginxManager(self.conf,self.log,self.db,self.global_cfg,self.proxy_mgr)
        self.token_mgr=TokenMgr(self.conf,self.log,self.db)
        self.user_mgr=UserMgr(self.conf,self.log,self.db)
        self.auth=Auth(self.conf,self.log,self.token_mgr,self.user_mgr,self.proxy_mgr)

        self.app=Flask(__name__)
        self.app.add_url_rule(self.conf.url_prefix+'/basic_auth',
                            'basic_auth',
                            self._basic_auth,
                            methods=['GET','POST'])
        self.app.add_url_rule(self.conf.url_prefix+'/token_auth',
                              'token_auth',
                              self._token_auth,
                              methods=['GET'])
        self.app.add_url_rule(self.conf.url_prefix+'/global-config',
                              'global_config',
                              self._global_config,
                              methods=['POST'])
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
  
    def _basic_auth(self):
        if request.method=='GET':
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN

        return self.auth.basic_auth(request.form.get('username'),
                            request.form.get('password'),
                            request.headers)

    def _token_auth(self):
        return self.auth.token_auth(request.headers,request.cookies)

    def _global_config(self):
        self.log.debug("global config request, %s"%(request.json))

        self.global_cfg.update(request.json)

        return jsonify({RestServer.RESULT:"ok"}),HTTP_OK

    def _sanity_check_proxy(self,request):
        proxy_del_list=[]
        
        req_uri_prefix_list=[]
        for user in request:
            req_uri_prefix_list+=map(lambda x:x[RestServer.URI_PREFIX],user[RestServer.WEB_INFO])

        for uri_prefix,web_url,port in self.proxy_mgr.list_proxy():
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
                                  map(lambda arg: arg[RestServer.URI_PREFIX],
                                        req[RestServer.WEB_INFO]))

    def _add_proxy_config(self):
        self.log.info("add_proxy_config %s"%request.json)

        if not request.json or not isinstance(request.json,list):
            return jsonify({RestServer.ERROR:HTTP_BAD_REQUEST_STR}),HTTP_BAD_REQUEST
       
        self._add_proxy_config_user(request.json)
       
        result,http_code=self._add_proxy_config_nginx(request.json)
        
        self._sanity_check(request.json)

        return result,http_code

    def _add_proxy_config_nginx(self,request):
        result=[]
        for user in request:
            for entry in user[RestServer.WEB_INFO]: 
                public_url=self.nginx_mgr.add_proxy(entry[RestServer.URI_PREFIX],
                                                    entry[RestServer.WEB_URL])

                item={RestServer.URI_PREFIX:entry[RestServer.URI_PREFIX],
                      RestServer.RESULT:'error',
                      RestServer.PUBLIC_URL:None}

                if public_url:
                    item[RestServer.RESULT]="ok"
                    item[RestServer.PUBLIC_URL]=public_url
                
                result.append(copy.deepcopy(item))

        return jsonify({RestServer.URL:result}),HTTP_OK

    def _add_token(self):
        self.log.debug("add_token %s"%request.json)

        if not request.json:
            return jsonify({"error":HTTP_BAD_REQUEST_STR}),HTTP_BAD_REQUEST

        self.token_mgr.add_token(request.json[RestServer.USER_NAME],request.json[RestServer.TOKEN]) 
        
        return jsonify({RestServer.RESULT:"ok"}),HTTP_OK

    def _del_proxy_config(self,uri_prefix):
        self.log.debug("del_proxy_config uri_prefix %s"%uri_prefix)
        
        self.nginx_mgr.del_proxy(uri_prefix)
        self.user_mgr.del_user_uri_prefix(uri_prefix)
        
        return jsonify({RestServer.RESULT:'ok'}),HTTP_OK

    def run_server(self):
        self.log.info('rest server run at %s:%d%s'%(self.conf.rest_server_address,
                                                  self.conf.rest_server_port,
                                                  self.conf.url_prefix))

        self.app.run(self.conf.rest_server_address,
                     self.conf.rest_server_port,
                     True)
