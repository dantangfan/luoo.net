#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
        name='luoo.net',
        version='0.10',
        description='luoo.net in terminal',
        author='dantangfan',
        author_email='dantangfan@github.com',
        url='http://github.com/dantangfan/luoo.net',
        license='LGPL',
        packages=find_packages(),
        zip_safe=True,
        install_requires=['BeautifulSoup'],
        entry_points={
            'console_scripts':[
                'luoo.net = luoo.luoo:main'
                ]
            },
        )
