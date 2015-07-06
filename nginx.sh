wget http://nginx.org/keys/nginx_signing.key
apt-key add nginx_signing.key
echo deb http://nginx.org/packages/ubuntu/ $(lsb_release -c -s) nginx >/etc/apt/sources.list.d/nginx.list
echo deb-src http://nginx.org/packages/ubuntu/ $(lsb_release -c -s) nginx >>/etc/apt/sources.list.d/nginx.list

apt-get remove nginx
apt-get remove nginx-common
apt-get purge nginx-common
apt-get update
apt-get install nginx
