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
            'pymongo',
            'netaddr',
            'netifaces'
    ],
    entry_points={
        'console_scripts':[
            'web-proxy=web_proxy.web_proxy:web_proxy_main',
            'web-proxy-wrapper=web_proxy.web_proxy_wrapper:main',
        ]
    }
)
