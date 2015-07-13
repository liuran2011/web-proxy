import urllib2
from http_codes import *
import json

class KeyStone(object):
    def __init__(self,conf,log):
        self.conf=conf
        self.log=log
    
    def verify_token(self,user_name,token):
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

    def get_token(self,username,password):
        headers={"Content-Type":"application/json"}
        url=self.conf.auth_url+"/tokens"
        data=json.dumps({
                            'auth':
                            {
                                'tenantName':username,
                                'passwordCredentials':
                                {
                                    'username':username,
                                    'password':password
                                }
                            }
                        })

        request=urllib2.Request(url,data,headers)
        try:
            sock=urllib2.urlopen(request)
            response_data=sock.read()
        except urllib2.HTTPError as e:
            self.log.error("request keystone %s failed.error %d"%(url,e.getcode()))
            return None
        except urllib2.URLError as e:
            self.log.error("request url %s failed. exception %s"%(url,e))
            return None

        res=json.loads(response_data)
        self.log.debug("keystone response %s"%(res))

        return res['access']['token']['id'];
