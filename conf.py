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
       
        if (not self.proxy_public_address
           or self.proxy_public_address=="127.0.0.1"  
           or self.proxy_public_address=="0.0.0.0"):
            print "proxy public address %s invalid."%(self.rest_server_address)
            sys.exit(1)
        
        if self.rest_server_address=="127.0.0.1":
            print "rest server address %s invalid"%(self.rest_server_address)
            sys.exit(1)
        
        if not self.mongodb_address:
            print "mongodb address %s invalid"%(self.mongodb_address)
            sys.exit(1)

    @property
    def mongodb_address(self):
        return self.args.mongodb_address

    @property
    def mongodb_port(self):
        return self.args.mongodb_port

    @property
    def nginx_config_path(self):
        return self.args.nginx_config_path

    @property
    def proxy_public_address(self):
        return self.args.proxy_public_address

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

    @property
    def auth_url(self):
        return self.args.auth_url

    def _parse_config_file(self,config_file,default_args):
        if (not os.path.exists(config_file) 
            or not os.path.isfile(config_file)):
            return

        parser=ConfigParser.ConfigParser()
        parser.read(config_file)
     
        if parser.has_section('nginx'):
            default_args.update(dict(parser.items('nginx')))

        if parser.has_section('rest'):
            default_args.update(dict(parser.items('rest')))

        if parser.has_section('log'):
            default_args.update(dict(parser.items('log')))

        if parser.has_section('proxy'):
            default_args.update(dict(parser.items('proxy')))

        if parser.has_section('mongo'): 
            default_args.update(dict(parser.items('mongo')))
        
        if parser.has_section('auth'):
            default_args.update(dict(parser.items('auth')))

    def _parse_arg(self):
        parser=argparse.ArgumentParser(add_help=False)
        parser.add_argument("--config_file",
                           default=WEB_PROXY_CONFIG_FILE,
                           type=str,
                           help="Web proxy program config file")
        
        default_args={
            "nginx_config_path":NGINX_CONFIG_PATH,
            "url_prefix":REST_API_URL_PREFIX,
            "log_level":WEB_PROXY_DEFAULT_LOG_LEVEL,
            "log_path":WEB_PROXY_DEFAULT_LOG_PATH,
            "rest_server_port":REST_API_PORT,
            "proxy_min_port":WEB_PROXY_MIN_PORT,
            "proxy_max_port":WEB_PROXY_MAX_PORT,
            "rest_server_address":REST_API_ADDRESS,
            "mongodb_port":MONGO_DB_PORT,
            "auth_url":AUTH_URL
        }

        args,remaing_argv=parser.parse_known_args()
        if args.config_file:
            self._parse_config_file(args.config_file,default_args)

        parser.set_defaults(**default_args)
        parser.add_argument("--nginx_config_path",
                           type=str,
                           help="Nginx config directory")
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
        parser.add_argument("--proxy_public_address",
                            type=str,
                            help="proxy public address")
        parser.add_argument("--mongodb_port",
                            type=int,
                            help="mongo db listen port")
        parser.add_argument("--mongodb_address",
                            type=str,
                            help="mongo db listen address")
        parser.add_argument("--auth_url",
                            type=str,
                            help="auth url of keystone")

        self.args=parser.parse_args(remaing_argv)
