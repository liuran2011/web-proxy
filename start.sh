#!/bin/bash

service nginx stop

ip netns exec web_proxy_netns service nginx start
ip netns exec web_proxy_netns ./web_proxy.py &
