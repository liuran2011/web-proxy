#!/bin/bash

log_file=/var/log/web_proxy/web_proxy_startup.log

while true;
do
    pid=$(pgrep contrail-vroute)
   
    if [ "x$pid" == "x" ]; then
        echo "contrail-vrouter-agent not start. try later..." >>$log_file
        sleep 1
        continue
    fi
   
    state=$(netstat -lt| grep 9090)

    if [ "x$state" == "x" ]; then
        echo "contrail-vrouter-agent 9090 port is not listen..." >>$log_file
        continue
    fi

    break
done

echo "contrail-vrouter-agent start ok. start web_proxy.py" >>$log_file
cd /home/web-proxy/web_proxy
../deploy.sh
../start.sh
