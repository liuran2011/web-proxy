import argparse
import os
import ConfigParser
import copy
import socket
import sys

from constants import *

class Config:
    def __init__(self):
        self._parse_arg()
       
        if not self.rest_server_address:
            print "rest server address invalid."
            sys.exit(1)

    @property
    def nginx_config_path(self):
        return self.args.nginx_config_path

    @property
    def proxy_config_path(self):
        return self.args.proxy_config_path

    @property
    def url_prefix(self):
        return self.args.url_prefix

    @property
    def log_level(self):
        return self.args.log_level

    @property
    def log_path(self):
        return self.args.log_path

    @property
    def rest_server_port(self):
        return self.args.rest_server_port
    
    @property
    def rest_server_address(self):
        return self.args.rest_server_address

    @property
    def proxy_min_port(self):
        return self.args.proxy_min_port

    @property
    def proxy_max_port(self):
        return self.args.proxy_max_port

    def _parse_config_file(self,config_file,default_args):
        parser=ConfigParser.ConfigParser()
        parser.read(config_file)
      
        default_args.update(dict(parser.items('nginx')))
        default_args.update(dict(parser.items('rest')))
        default_args.update(dict(parser.items('log')))
        default_args.update(dict(parser.items('proxy')))

    def _parse_arg(self):
        parser=argparse.ArgumentParser(add_help=False)
        parser.add_argument("--config_file",
                           default=WEB_PROXY_CONFIG_FILE,
                           type=str,
                           help="Web proxy program config file")
        
        default_args={
            "nginx_config_path":NGINX_CONFIG_PATH,
            "proxy_config_path":NGINX_WEB_PROXY_PATH,
            "url_prefix":REST_API_URL_PREFIX,
            "log_level":WEB_PROXY_DEFAULT_LOG_LEVEL,
            "log_path":WEB_PROXY_DEFAULT_LOG_PATH,
            "rest_server_port":REST_API_PORT,
            "proxy_min_port":WEB_PROXY_MIN_PORT,
            "proxy_max_port":WEB_PROXY_MAX_PORT
        }

        args,remaing_argv=parser.parse_known_args()
        if args.config_file:
            self._parse_config_file(args.config_file,default_args)

        parser.set_defaults(**default_args)
        parser.add_argument("--nginx_config_path",
                           type=str,
                           help="Nginx config directory")
        parser.add_argument("--proxy_config_path",
                           type=str,
                           help="path to store proxy file used by nginx")
        parser.add_argument("--url_prefix",
                           type=str,
                           help="url prefix add to rest server request")
        parser.add_argument("--log_level",
                           type=str,
                           help="web proxy log level")
        parser.add_argument("--log_path",
                            type=str,
                            help="path to store log of web proxy")
        parser.add_argument("--rest_server_address",
                            type=str,
                            help="bind address of rest server")
        parser.add_argument("--rest_server_port",
                            type=int,
                            help="listen port of rest server")
        parser.add_argument("--proxy_min_port",
                            type=int,
                            help="proxy min port")
        parser.add_argument("--proxy_max_port",
                            type=int,
                            help="proxy max port")
        self.args=parser.parse_args(remaing_argv)
