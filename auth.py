from http_codes import *
import urllib2

class Auth(object):
    def __init__(self,log,token_mgr,user_mgr):
        self.log=log
        self.token_mgr=token_mgr
        self.user_mgr=user_mgr

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
        
        return HTTP_OK_STR,HTTP_OK

    def auth(http_headers):
        if not http_headers:
            return HTTP_INTERNAL_ERROR_STR,HTTP_INTERNAL_ERROR

        origin_uri=http_headers.get('X-Origin-URI')
        if not origin_uri:
            return HTTP_INTERNAL_ERROR_STR,HTTP_INTERNAL_ERROR

        ret=re.match(".*username=([^?&]*).*token=([^?&]*)",origin_uri)
        if not ret or len(ret.groups())<2:
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN

        user_name=ret.groups()[0]
        md5=ret.groups()[1]

        #TODO check user if can access this service.
        token=self.token_mgr.find_token_from_md5(md5)
        if not token:
            return HTTP_FORBIDEN_STR,HTTP_FORBIDEN
       
        return self._auth_with_keystone(user_name,token)        
