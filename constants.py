WEB_PROXY_CONFIG_PATH="/etc/web_proxy"
WEB_PROXY_CONFIG_FILE=WEB_PROXY_CONFIG_PATH+"/web_proxy.conf"

WEB_PROXY_DEFAULT_LOG_LEVEL="notice"
WEB_PROXY_DEFAULT_LOG_PATH="/var/log/web_proxy"

WEB_PROXY_PORT=10000
WEB_PROXY_MIN_PORT=22222
WEB_PROXY_MAX_PORT=33333

NGINX_CONFIG_PATH="/etc/nginx"

NGINX_WEB_PROXY_PATH="/var/run/web_proxy"
NGINX_WEB_PROXY_FILE_NAME="web_proxy"
NGINX_WEB_PROXY_FILE_TEMPLATE="""
    server {
        listen %d;
        error_log %s %s;
        server_name %s;

        location / {
            proxy_pass %s;
        }
    }
    """

REST_API_PORT=9999
REST_API_URL_PREFIX='/web_proxy/api/v1.0'
REST_API_ADDRESS="0.0.0.0"

MONGO_DB_PORT=27017
