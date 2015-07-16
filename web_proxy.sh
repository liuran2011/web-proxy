#!/bin/bash

log_file=/var/log/web_proxy/web_proxy_startup.log

while true;
do
    pid=$(pgrep contrail-vroute)
   
    if [ "x$pid" == "x" ]; then
        echo "contrail-vrouter-agent not start. try later..." >>$log_file
        sleep 1
    else
        echo "contrail-vrouter-agent start ok. start web_proxy.py" >>$log_file
        cd /home/web-proxy
        ./deploy.sh
        ./start.sh
        break
    fi
done
