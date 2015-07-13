#! /usr/bin/env python

import sys
import os
import netaddr
import argparse
from constants import *
import ConfigParser

sys.path.append('/usr/lib/python2.7/dist-packages/contrail_vrouter_api/gen_py')
sys.path.append('/usr/share/contrail-utils')

from vnc_api import vnc_api
import cfgm_common.exceptions

import instance_service.ttypes
from contrail_utils import vrouter_rpc, \
     uuid_from_string, uuid_array_to_str, \
     new_interface_name, sudo, link_exists_func, ProcessExecutionError, \
     format_dict

class ContrailVethPort(object):
    def __init__(self, *argv, **args):
        self._parse_args()
            
        self.vnc_client = None

    def _parse_config_file(self,file,args):
        if (not os.path.exists(file)
            or not os.path.isfile(file)):
            return
        
        parser=ConfigParser.ConfigParser()
        parser.read(file)
        
        if parser.has_section('auth'):
            args.update(dict(parser.items('auth')))
        
        if parser.has_section('contrail'):
            args.update(dict(parser.items('contrail')))
 
    def _parse_args(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "--config-file",
            default=WEB_PROXY_CONFIG_FILE,
            help=("configure file.  Default:"+WEB_PROXY_CONFIG_FILE))  
        
        default_args={
            "api_server":CONTRAIL_API_SERVER,
            "api_port":CONTRAIL_API_PORT,
            "project":CONTRAIL_PROJECT,
            "netns":CONTRAIL_NETNS,
            "auth_url":AUTH_URL,
            "vm_name":CONTRAIL_VM_NAME,
            "net_name":CONTRAIL_NET_NAME
        }

        args,remain_argv=parser.parse_known_args()
        if args.config_file:
            self._parse_config_file(args.config_file,default_args)

        parser.set_defaults(**default_args)
        parser.add_argument(
            "--api-server",
            help="API server address. Default:"+CONTRAIL_API_SERVER)
        parser.add_argument(
            "--api-port",
            help="API server port. Default:%d"%CONTRAIL_API_PORT)
        parser.add_argument(
            "--project",
            help="OpenStack project name. Default:"+CONTRAIL_PROJECT)
        parser.add_argument(
            "--delete", action="store_true",
            help="Delete the virtual machine and network")
        parser.add_argument(
            "--format",
            default="table",
            help="Format of output values: table, shell, json, python")
        parser.add_argument(
            "--auth_url",
            help="openstack auth url")  
        parser.add_argument(
            "--netns",
            help=("Name of the network namespace to put the veth interface in."
                  + "   Default: virtual network name"))
        parser.add_argument(
            "--vm_name", help="Name of virtual machine to create to own the port")
        parser.add_argument(
            "--net_name", 
            help=("Name of virtual network to attach veth interface to."
                  + "  Will be created if it doesn't already exist"))
        
        self.args=vars(parser.parse_args(remain_argv))

    def vnc_connect(self):
        if not self.vnc_client:
            self.vnc_client = vnc_api.VncApi(
                api_server_host=self.args['api_server'],
                api_server_port=self.args['api_port'],
                auth_url=self.args['auth_url'])
        return self.vnc_client
        
    def create(self):
        # remember what to clean up if things go wrong
        port_created = False
        veth_created = False
        netns_created = False
        ip_created = False
        vmi_created = False
        vnet_created = False
        vm_created = False

        try:
            vnc_client = self.vnc_connect()

            proj_fq_name = self.args['project'].split(':')

            vm_fq_name = [ self.args['vm_name']]

            try:
                vm = vnc_client.virtual_machine_read(fq_name = vm_fq_name)
            except cfgm_common.exceptions.NoIdError:
                # create vm if necessary
                vm = vnc_api.VirtualMachine(self.args['vm_name'],
                                            fq_name=vm_fq_name)
                vnc_client.virtual_machine_create(vm)
                vm = vnc_client.virtual_machine_read(fq_name = vm_fq_name)
                vm_created = True
    
            # find the network
            vnet_fq_name = proj_fq_name + [ self.args['net_name'] ]
            vnet_created = False
            vnet = vnc_client.virtual_network_read(fq_name = vnet_fq_name)

            # find or create the vmi
            vmi_fq_name = vm.fq_name + ['0']
            vmi_created = False
            try:
                vmi = vnc_client.virtual_machine_interface_read(
                    fq_name = vmi_fq_name)
            except cfgm_common.exceptions.NoIdError:
                vmi = vnc_api.VirtualMachineInterface(
                    parent_type = 'virtual-machine',
                    fq_name = vmi_fq_name)
                vmi_created = True
            vmi.set_virtual_network(vnet)
            if vmi_created:
                vnc_client.virtual_machine_interface_create(vmi)
            else:
                vnc_client.virtual_machine_interface_update(vmi)
            # re-read the vmi to get its mac addresses
            vmi = vnc_client.virtual_machine_interface_read(
                fq_name = vmi_fq_name)
            # create an IP for the VMI if it doesn't already have one
            ips = vmi.get_instance_ip_back_refs()
            if not ips:
                ip = vnc_api.InstanceIp(vm.name + '.0')
                ip.set_virtual_machine_interface(vmi)
                ip.set_virtual_network(vnet)
                ip_created = vnc_client.instance_ip_create(ip)

            # Create the veth port.  Create a veth pair.  Put one end
            # in the VMI port and the other in a network namespace
            
            # get the ip, mac, and gateway from the vmi
            ip_uuid = vmi.get_instance_ip_back_refs()[0]['uuid']
            ip = vnc_client.instance_ip_read(id=ip_uuid).instance_ip_address
            mac = vmi.virtual_machine_interface_mac_addresses.mac_address[0]
            subnet = vnet.network_ipam_refs[0]['attr'].ipam_subnets[0]
            gw = subnet.default_gateway
            dns = gw # KLUDGE - that's the default, but some networks
                     # have other DNS configurations
            ipnetaddr = netaddr.IPNetwork("%s/%s" %
                                          (subnet.subnet.ip_prefix,
                                           subnet.subnet.ip_prefix_len))
            
            # set up the veth pair with one part for vrouter and one
            # for the netns

            # find a name that's not already used in the default or
            # netns namespaces
            netns=self.args['netns']
            link_exists = link_exists_func('', netns)
            veth_vrouter = new_interface_name(suffix=vnet.uuid, prefix="ve1",
                                              exists_func=link_exists)
            veth_host = new_interface_name(suffix=vnet.uuid, prefix="ve0",
                                           exists_func=link_exists)
            
            sudo("ip link add %s type veth peer name %s",
                 (veth_vrouter, veth_host))
            veth_created = True
            try:
                sudo("ip netns add %s", (netns,))
                netns_created = True
            except ProcessExecutionError:
                pass
            
            sudo("ip link set %s netns %s",
                 (veth_host, netns))
            sudo("ip netns exec %s ip link set dev %s address %s",
                 (netns, veth_host, mac))
            sudo("ip netns exec %s ip address add %s broadcast %s dev %s",
                 (netns,
                  ("%s/%s" % (ip, subnet.subnet.ip_prefix_len)),
                  ipnetaddr.broadcast, veth_host))
            sudo("ip netns exec %s ip link set dev %s up",
                 (netns, veth_host))
            sudo("ip netns exec %s route add default gw %s dev %s",
                 (netns, gw, veth_host))
            sudo("ip link set dev %s up", (veth_vrouter,))

            # make a namespace-specific resolv.conf
            resolv_conf = "/etc/netns/%s/resolv.conf" % netns
            resolv_conf_body = "nameserver %s\n" % dns
            sudo("mkdir -p %s", (os.path.dirname(resolv_conf),))
            sudo("tee %s", (resolv_conf,), process_input=resolv_conf_body)

            # finally, create the Contrail port
            port = instance_service.ttypes.Port(
                uuid_from_string(vmi.uuid),
                uuid_from_string(vm.uuid), 
                veth_vrouter,
                ip,
                uuid_from_string(vnet.uuid),
                mac,
                )
            rpc = vrouter_rpc()
            rpc.AddPort([port])
            port_created = True
            
            return(dict(
                port_id = uuid_array_to_str(port.port_id),
                vm_id = vm.uuid,
                net_id = vnet.uuid,
                vmi_id = vmi.uuid,
                veth = veth_host,
                netns = netns,
                ip = ip,
                mac = mac,
                gw = gw,
                dns = dns,
                netmask = str(ipnetaddr.netmask),
                broadcast = str(ipnetaddr.broadcast),
                ))

        except:
            # something went wrong, clean up
            if port_created:
                rpc.DeletePort(port.port_id)
            if veth_created:
                sudo("ip link delete %s", (veth_vrouter,),
                     check_exit_code=False)
            if netns_created:
                sudo("ip netns delete %s", (netns,), check_exit_code=False)
            if ip_created:
                vnc_client.instance_ip_delete(id=ip_created)
            if vmi_created:
                vnc_client.virtual_machine_interface_delete(id=vmi.uuid)
            if vnet_created:
                vnc_client.virtual_network_delete(id=vnet.uuid)
            if vm_created:
                vnc_client.virtual_machine_delete(id=vm.uuid)
            raise

    def delete(self):
        """Delete a vm and its vmi."""
        vnc_client = self.vnc_connect()
        
        proj_fq_name = self.args['project'].split(':')
        vm_fq_name = proj_fq_name + [ self.args['vm_name'] ]
        try:
            # delete all dependent VMIs and IPs then delete the VM
            vm = vnc_client.virtual_machine_read(fq_name = vm_fq_name)
            for vmi in vm.get_virtual_machine_interfaces():
                try:
                    vmi = vnc_client.virtual_machine_interface_read(
                        id=vmi['uuid'])
                    for ip in vmi.get_instance_ip_back_refs():
                        try:
                            vnc_client.instance_ip_delete(id=ip['uuid'])
                        except cfgm_common.exceptions.NoIdError:
                            pass
                    vnc_client.virtual_machine_interface_delete(id=vmi.uuid)
                except cfgm_common.exceptions.NoIdError:
                    pass
            vnc_client.virtual_machine_delete(id=vm.uuid)
        except cfgm_common.exceptions.NoIdError:
            pass

        # TODO: delete the veth, but there's no way to find the local
        # vrouter port.  The vrouter API has AddPort and DeletePort,
        # but no GetPort
    
    def main(self):
        """run from command line"""
        if self.args['delete']:
            self.delete()
        else:
            ret = self.create()
            print format_dict(ret, self.args['format'])

def main():
    ContrailVethPort().main()

if __name__ == '__main__':
    main()
