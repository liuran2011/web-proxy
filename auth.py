from http_codes import *
import urllib2
import re
from flask import make_response

class Auth(object):
    def __init__(self,conf,log,token_mgr,user_mgr):
        self.log=log
        self.token_mgr=token_mgr
        self.user_mgr=user_mgr
        self.conf=conf

    def _auth_with_keystone(self,user_name,token):
        headers={"Content-Type":"application/json","X-Auth-Token":token}
        url=self.conf.auth_url+"/tokens/"+token
        request=urllib2.Request(url,None,headers)

        try:
            res=urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            self.log.error("request keystone %s failed, error %d"%(url,e.getcode()))
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN
        except urllib2.URLError as e:
            self.log.error("request url %s failed. exception %s"%(url,e))
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN

        self.log.debug("user:%s auth with keystone ok."%(user_name))

        return HTTP_OK_STR,HTTP_OK

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
       
        return self._auth_with_keystone(user_name,token)   

