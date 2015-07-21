import hashlib
import urlparse
import netifaces

class MD5(object):
    @staticmethod
    def get(data):
        md5=hashlib.md5()
        md5.update(data)
        return md5.hexdigest()

class URL(object):
    @staticmethod
    def get_root(url):
        url_comps=urlparse.urlparse(url)  
        path_segs=url_comps.path.split('/')
        if len(path_segs)<2:
            return ""

        return path_segs[1]

    @staticmethod
    def get_base(url):
        url_comps=urlparse.urlparse(url)
        
        return url_comps.scheme+"://"+url_comps.netloc

    @staticmethod
    def get_comps(url):
        url_comps=urlparse.urlparse(url)
        net_locs=url_comps.netloc.split(':')

        if len(net_locs)==2:
            return url_comps.scheme,net_locs[0],int(net_locs[1])

        return url_comps.scheme,net_locs[0],None

    @staticmethod
    def get_scheme(url):
        return urlparse.urlparse(url).scheme 

    @staticmethod
    def get_path(url):
        return urlparse.urlparse(url).path

class Net(object):
    @staticmethod
    def intf_exist(name):
        return name in netifaces.interfaces()

    @staticmethod
    def get_ip(phy_if):
        try:
            addr_info=netifaces.ifaddresses(phy_if)[netifaces.AF_INET][0]
            return addr_info['addr'],addr_info['netmask']
        except:
            return None,None

