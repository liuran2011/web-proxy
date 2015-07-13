from setuptools import setup,find_packages

setup(
    name="web_proxy",
    version="1.0",
    author="liuran",
    author_email="liuran@fnic.cn",
    description="web proxy for contrail",
    packages=find_packages(),
    install_requires=[
            'gevent',
            'flask',
            'pymongo'
    ],
    package_data={'':['*.html','*.css']},
    entry_points={
        'console_scripts':[
            'web-proxy=web_proxy.web_proxy:web_proxy_main',
            'contrail-veth-port=web_proxy.contrail_veth_port:main',
        ]
    }
)
