#!/bin/bash

ip netns exec web_proxy_netns service nginx start
ip netns exec web_proxy_netns service mongodb start
ip netns exec web_proxy_netns /home/web-proxy/web_proxy.py
