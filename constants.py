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

        root %s;

        error_page 403 /d6f4f78b-cb93-4af4-ba76-8c6c741ce377.html;

        proxy_intercept_errors on;

        location /d6f4f78b-cb93-4af4-ba76-8c6c741ce377.html {
        }

        location /css/d6f4f78b-cb93-4af4-ba76-8c6c741ce377.css {
        }

        location /d6f4f78b-cb93-4af4-ba76-8c6c741ce377/auth {
            proxy_pass http://%s:%d/basic_auth;
        }

        location / {
            auth_request /token_auth;
            proxy_pass %s;

            if ($arg_token) {
                add_header Set-Cookie token=$arg_token;
            }
        }

        location /token_auth {
            proxy_pass http://%s:%d;
            proxy_pass_request_body off;
            proxy_set_header Content-Length "";
            proxy_set_header X-Origin-URI $request_uri;
        }
    }
    """

REST_API_PORT=9999
REST_API_URL_PREFIX='/web_proxy/api/v1.0'
REST_API_ADDRESS="0.0.0.0"

MONGO_DB_PORT=27017

AUTH_URL="http://localhost:5000/v2.0"

FORBIDEN_PAGE_UUID="d6f4f78b-cb93-4af4-ba76-8c6c741ce377"
