
./contrail_veth_port.py --project default-domain:admin --netns web_proxy_netns web_proxy_vm public

brctl addbr br0
brctl addif br0 em1
ifconfig br0 10.10.7.200/16 up
ifconfig em1 0.0.0.0

ip link add vewebproxyout type veth peer name ewebproxyin
brctl addif br0 vewebproxyout
ifconfig vewebproxyout up
ip link set vewebproxyin netns web_proxy_netns
ip netns exec web_proxy_netns ifconfig vewebproxyin 10.10.7.247/16 up


