#!/usr/bin/env python

import os
import sys
from constants import *
from utils import Net
import ConfigParser
from contrail_veth_port import ContrailVethPort
import time

class WebProxyWrapper(object):
    def __init__(self):
        self._config={
            "bridge_name":DEFAULT_BRIDGE_NAME,
            "netns":CONTRAIL_NETNS
        }

        cfg_file=WEB_PROXY_CONFIG_FILE
        if (not os.path.exists(cfg_file) 
            or not os.path.isfile(cfg_file)):
            print "config file %s not exist."%(cfg_file)
            sys.exit(1)

        self._parse_config(cfg_file)

        phy_if=self._config.get('physical_interface',None)
        if not phy_if or phy_if=="":
            print "physical_interface config error in %s"%(cfg_file)
            sys.exit(1)

        if not Net.intf_exist(phy_if):
            print "physical interface %s not exist"%(phy_if)
            sys.exit(1)

        proxy_public_address=self._config.get('proxy_public_address',None) 
        if (not proxy_public_address 
            or proxy_public_address == "127.0.0.1" 
            or proxy_public_address == "0.0.0.0"):
            print "invalid proxy_public_address in config file %s"%(cfg_file)
            sys.exit(1)

        physical_address=self._config.get('physical_interface_address',None)
        if (not physical_address 
            or physical_address=="127.0.0.1" 
            or physical_address=="0.0.0.0"):
            print "invalid physical address %s"%(physical_address)
            sys.exit(1)

        self._veth=ContrailVethPort()

    def _parse_config(self,cfg_file):
        parser=ConfigParser.ConfigParser()
        parser.read(cfg_file)
       
        sec='default'
        if parser.has_section(sec):
            self._config.update(dict(parser.items(sec)))

        sec='contrail'
        item='netns'
        if parser.has_section(sec):
            self._config[item]=parser.get(sec,item)
       
        sec='proxy'
        item='proxy_public_address'
        if parser.has_section(sec):
            self._config[item]=parser.get(sec,item)
        
    def _add_bridge(self):
        br=self._config['bridge_name']
        cmd="brctl addbr "+br
        os.system(cmd)

        cmd="brctl addif %s %s"%(br,self._config['physical_interface'])
        os.system(cmd)

        cmd="brctl addif %s vewebproxyout"%(br)
        os.system(cmd)

    def _add_veth(self):
        cmd="ip link add vewebproxyout type veth peer name vewebproxyin"
        os.system(cmd)

    def _intf_up(self):
        cmd="ifconfig vewebproxyout up"
        os.system(cmd)
        
        cmd="ifconfig %s up"%(self._config['physical_interface'])
        os.system(cmd)

        cmd="ifconfig %s up"%(self._config['bridge_name'])
        os.system(cmd)

        netns=self._config['netns']
        cmd="ip netns exec %s ifconfig vewebproxyin up"%(netns)
        os.system(cmd)

        cmd="ip netns exec %s ifconfig lo up"%(netns)
        os.system(cmd)

    def _assign_address(self):
        cmd="ifconfig %s 0.0.0.0"%(self._config['physical_interface'])
        os.system(cmd)

        cmd="ifconfig %s %s netmask %s up"%(self._config['bridge_name'],
                                    self._config['physical_interface_address'],
                                    self._config['physical_interface_netmask'])
        os.system(cmd)

        cmd="ip netns exec %s ifconfig vewebproxyin %s/16 up"%(self._config['netns'],
                        self._config['proxy_public_address'])
        os.system(cmd)

    def _netns_proc(self):
        netns=self._config['netns']
        cmd="ip link set vewebproxyin netns "+netns
        os.system(cmd)

    def _contrail_veth_port_run(self):
        while True:
            try:    
                self._veth.main()
                break
            except Exception as e:
                print e
                time.sleep(1)
                continue

    def _nginx_restart(self):
        cmd="service nginx stop"
        os.system(cmd)

        cmd="ip netns exec %s service nginx start"%(self._config['netns'])
        os.system(cmd)

    def run(self):
        self._contrail_veth_port_run()   
        self._add_veth()
        self._netns_proc()
        self._add_bridge()
        self._assign_address()
        self._intf_up()
        self._nginx_restart()

        os.execv('/sbin/ip',['ip','netns','exec',self._config['netns'],'/usr/bin/web-proxy'])

def main():
    w=WebProxyWrapper()
    w.run()
    
if __name__=="__main__":
    main() 
