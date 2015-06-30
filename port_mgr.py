class PortMgr(object):
    _port_map={}
    _port_list=[]

    def __init__(self,log,conf):
        self.conf=conf
        self.log=log
        
        _port_list=[0 for x in range(self.conf.proxy_min_port,self.conf.proxy_max_port)]

    def _set_port_inuse(self,port):
        _port_list[port-self.conf.proxy_min_port]=1

    def _alloc_port(self):
        try:
            index=_port_list.index(0)
            return index+self.conf.proxy_min_port
        except ValueError as e:
            self.log.error("port exausted.")
            return None

    def _free_port(self,port):
        _port_list[port-self.proxy_min_port]=0

    def alloc_port(self,instance_name):
        port=_port_map.get(instance_name)
        if port:
            return port

        port=self._alloc_port() 
        if not port:
            return None

        _port_map[instance_name]=port

        return port

    def free_port(self,instance_name):
        port=_port_map.get(instance_name)
        if not port:
            return

        self._free_port(port)
        d.pop(instance_name)
    
    def map_port(self,uri_prefix,port):
        inuse_port=_port_map.get(uri_prefix)   
        if inuse_port and inuse_port!=port:
            self.log.warning("uri_preifx:%s already has port:%d"%(uri_prefix,port))
            return

        self._set_port_inuse(port)
        _port_map[uri_prefix]=port
    
    def port_exist(self,uri_prefix):
        port=_port_map.get(uri_prefix)
        if port:
            return port

        return None
