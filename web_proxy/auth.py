from http_codes import *
import re
from keystone import KeyStone
from flask import redirect
import urlparse
from utils import MD5
from constants import *
import urllib2

class Auth(object):
    def __init__(self,conf,log,token_mgr,user_mgr,proxy_mgr):
        self.log=log
        self.token_mgr=token_mgr
        self.user_mgr=user_mgr
        self.proxy_mgr=proxy_mgr
        self.conf=conf
        self.keystone=KeyStone(self.conf,self.log)

    def _get_token_id(self,url,cookie):
        ret=re.match(".*token=([^?&]*)",url)
        if ret:
            return ret.groups()[0]

        self.log.debug("auth url: %s do not has token. get from cookie."%(url))
       
        ret=cookie.get('token',None)
        if ret:
            return ret

        self.log.debug("cookie %s do not has token"%(cookie))

        return None
       
    def token_auth(self,http_headers,cookie):
        if not http_headers:
            self.log.error("auth request has no http headers")
            return HTTP_INTERNAL_ERROR_STR,HTTP_INTERNAL_ERROR

        origin_uri=http_headers.get('X-Origin-URI',None)
        if not origin_uri:
            self.log.error("auth request http header:%s has no X-Origin-URI"%(http_headers))
            return HTTP_INTERNAL_ERROR_STR,HTTP_INTERNAL_ERROR

        origin_port=http_headers.get('X-Origin-Port',None)
        if not origin_port:
            self.log.error("auth request http header %s has no X-Origin-Port"%(http_headers))
            return HTTP_INTERNAL_ERROR_STR,HTTP_INTERNAL_ERROR

        token_id=self._get_token_id(origin_uri,cookie)
        if not token_id:
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN

        user_name,token=self.token_mgr.find_token(token_id)
        if not token:
            self.log.debug("auth token_id:%s find token failed"%(token_id))
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN
     
        uri_prefix=self.proxy_mgr.find_uri_prefix(int(origin_port))
        if not uri_prefix:
            self.log.debug("auth port:%s find uri_prefix failed"%(origin_port))
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN

        if not self.user_mgr.user_has_uri_prefix(user_name,uri_prefix):
            self.log.debug("user %s can't access %s"%(user_name,uri_prefix))
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN

        return self.keystone.verify_token(user_name,token)   

    def basic_auth(self,username,password,headers):
        if not len(username) or not len(password):
            self.log.error("username or password is empty")
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN
        
        host=headers.get('X-Origin-Host',None)
        port=headers.get('X-Origin-Port',None)
        if not host or not port:
            self.log.error("X-Origin-Host or X-Origin-Port not in headers:%s"%(headers))
            return HTTP_INTERNAL_ERROR_STR,HTTP_INTERNAL_ERROR

        web_url=self.proxy_mgr.find_web_url(int(port))
        if not web_url:
            self.log.error("find web_url from port:%s failed"%(port))
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN

        token=self.keystone.get_token(username,password)
        if not token:
            self.log.error("get token from keystone failed.")
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN

        self.log.info("get token from keystone success.")

        self.token_mgr.add_token(username,token)

        url_comps=urlparse.urlparse(web_url)
        url="http://"+host+":"+port+url_comps.path+"?username="+urllib2.quote(username.encode('utf8'))+"&token="+MD5.get(token)
        self.log.info("redirect to :%s"%url)

        return redirect(url)

    def get_token(self,username,password):
        return self.keystone.get_token(username,password)
