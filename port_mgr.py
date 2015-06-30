class PortMgr(object):
    def __init__(self,log,conf):
        self.conf=conf
        self.log=log
        
        self.port_list=[0 for x in range(self.conf.proxy_min_port,self.conf.proxy_max_port)]
        self.port_map={}

    def _set_port_inuse(self,port):
        self.port_list[port-self.conf.proxy_min_port]=1

    def _alloc_port(self):
        try:
            index=self.port_list.index(0)
            return index+self.conf.proxy_min_port
        except ValueError as e:
            self.log.error("port exausted.")
            return None

    def _free_port(self,port):
        self.port_list[port-self.proxy_min_port]=0

    def alloc_port(self,instance_name):
        port=self.port_map.get(instance_name)
        if port:
            return port

        port=self._alloc_port() 
        if not port:
            return None

        self.port_map[instance_name]=port

        return port

    def free_port(self,instance_name):
        port=self.port_map.get(instance_name)
        if not port:
            return

        self._free_port(port)
        d.pop(instance_name)
    
    def map_port(self,uri_prefix,port):
        inuse_port=self.port_map.get(uri_prefix)   
        if inuse_port and inuse_port!=port:
            self.log.warning("uri_preifx:%s already has port:%d"%(uri_prefix,port))
            return

        self._set_port_inuse(port)
        self.port_map[uri_prefix]=port
    
    def find_port(self,uri_prefix):
        port=self.port_map.get(uri_prefix)
        if port:
            return port

        return None
