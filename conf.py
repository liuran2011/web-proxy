import argparse
import os
import ConfigParser
import copy

from constants import *

class Config:
    def __init__(self):
        self._parse_arg()
        
        if os.path.exists(self.config_file):
            self._parse_config_file()

    @property
    def config_file(self):
        return self.args['config_file']

    @property
    def nginx_config_path(self):
        return self.args['nginx_config_path']

    @property
    def proxy_config_path(self):
        return self.args['proxy_config_path']

    @property
    def url_prefix(self):
        return self.args['url_prefix']

    @property
    def log_level(self):
        return self.args['log_level']

    @property
    def log_path(self):
        return self.args['log_path']

    @property
    def rest_server_port(self):
        return self.args['rest_server_port']

    @property
    def proxy_port(self):
        return self.args['proxy_port']

    def _parse_config_file_nginx(self,parser,section):
        opt='config_path'
        if parser.has_option(opt):
            self.nginx_config_path=parser.get(section,opt)
    
    def _parse_config_file_rest(self,parser,section):
        opt='url_prefix'
        if parser.has_option(opt):
            self.url_prefix=parser.get(section,opt)

        opt='port'
        if parser.has_option(opt):
            self.rest_server_port=parser.get(section,opt)

    def _parse_config_file_log(self,section):
        opt='level'
        if parser.has_option(opt):
            self.log_level=parser.get(section,opt)
        
        opt='path'
        if parser.has_option(opt):
            self.log_path=parser.get(section,opt)

    def _parse_config_file_proxy(self,parser,section):
        opt='port'
        if parser.has_option(opt):
            self.proxy_port=parser.get(section,opt)
        
        opt='config_path'
        if parser.has_option(opt):
            self.proxy_config_path=parser.get(section,opt)

    def _parse_config_file(self):
        parser=ConfigParser.ConfigParser()
        parser.read(self.config_file)
        
        section_parser={'nginx':self._parse_config_file_nginx,
                        'rest_server':self._parse_config_file_rest,
                        'log':self._parse_config_file_log,
                        'proxy':self._parse_config_file_proxy}
        
        for sec in filter(lambda section: section in section_parser,parser.sections):
            section_parser[sec](parser,section)
       
    def _parse_arg(self):
        parser=argparse.ArgumentParser()
        parser.add_argument("--config_file",
                           default=WEB_PROXY_CONFIG_FILE,
                           type=str,
                           help="Web proxy program config file")
        parser.add_argument("--nginx_config_path",
                           default=NGINX_CONFIG_PATH,
                           type=str,
                           help="Nginx config directory")
        parser.add_argument("--proxy_config_path",
                           default=NGINX_WEB_PROXY_PATH,
                           type=str,
                           help="path to store proxy file used by nginx")
        parser.add_argument("--url_prefix",
                           default=REST_API_URL_PREFIX,
                           type=str,
                           help="url prefix add to rest server request")
        parser.add_argument("--log_level",
                           default=WEB_PROXY_DEFAULT_LOG_LEVEL,
                           type=str,
                           help="web proxy log level")
        parser.add_argument("--log_path",
                            default=WEB_PROXY_DEFAULT_LOG_PATH,
                            type=str,
                            help="path to store log of web proxy")
        parser.add_argument("--rest_server_port",
                            default=REST_API_PORT,
                            type=int,
                            help="listen port of rest server")
        parser.add_argument("--proxy_port",
                            default=WEB_PROXY_PORT,
                            type=int,
                            help="proxy port of web proxy")
        self.args=copy.deepcopy(parser.parse_args().__dict__)

    def get(self):
        pass

