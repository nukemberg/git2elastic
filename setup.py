#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='git2elasitc',
    version='0.0.1',
    author='Avishai Ish-Shalom',
    author_email='avishai.ishshalom@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'git2elastic = git2elastic:git2elastic'
        ]
    },
    install_requires=[
        'elasticsearch',
        'click',
        'gitpython'
        ]
    )
