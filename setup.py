# coding:utf8
from setuptools import setup

setup(
    name='TetrisBattle',
    version='1.0',
    packages=['TetrisBattle'],
    python_requires=">=3.6",
    install_requires=[
        'pygame>=1.9.4',
        'numpy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
)
