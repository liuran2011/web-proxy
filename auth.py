from http_codes import *
import re
from keystone import KeyStone
from flask import redirect,url_for,abort

class Auth(object):
    def __init__(self,conf,log,token_mgr,user_mgr):
        self.log=log
        self.token_mgr=token_mgr
        self.user_mgr=user_mgr
        self.conf=conf
        self.keystone=KeyStone(self.conf,self.log)

    def _get_token_id(self,url,cookie):
        ret=re.match(".*token=([^?&]*)",url)
        if ret:
            return ret.groups()[0]

        self.log.debug("auth url: %s do not has token"%(url))
        
        return cookie.get('token',None)
       
    def auth(self,http_headers,cookie):
        if not http_headers:
            self.log.debug("auth request has no http headers")
            return HTTP_INTERNAL_ERROR_STR,HTTP_INTERNAL_ERROR

        origin_uri=http_headers.get('X-Origin-URI',None)
        if not origin_uri:
            self.log.debug("auth request http header:%s has no X-Origin-URI"%(http_headers))
            return HTTP_INTERNAL_ERROR_STR,HTTP_INTERNAL_ERROR

        token_id=self._get_token_id(origin_uri,cookie)
        if not token_id:
            self.log.debug("cookie %s do not has token"%(cookie))
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN

        #TODO check user if can access this service.
        user_name,token=self.token_mgr.find_token(token_id)
        if not token:
            self.log.debug("auth user:%s token_id:%s find token failed"%(user_name,token_id))
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN
       
        return self.keystone.verify_token(user_name,token)   

    def _redirect_url(self,url):
        return redirect(url_for(url))

    def basic_auth(self,username,password,headers):
        token=self.keystone.get_token(username,password)
        if not token:
            self.log.error("get token from keystone failed.")
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN

        self.token_mgr.add_token(username,token)

        referer=headers.get('Referer',None)
        if not referer:
            self.log.error("http header %s do not have referer"%(headers))
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN

        return redirect(url_for('/?token='+token))

