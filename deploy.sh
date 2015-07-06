brctl addbr br0
brctl addif br0 em1
ifconfig br0 10.10.7.200/24 up

ip link add vewebproxyout type veth peer name ewebproxyin
brctl addif br0 vewebproxyout
ifconfig vewebproxyout up
ip link set vewebproxyin netns web_proxy_netns

