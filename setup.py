# -*- coding: utf-8 -*-
from io import open
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="taqu",
    version="1.0.0",
    description="Taqu Task Queue system",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/lietu/taqu",
    author="Janne Enberg",
    author_email="janne.enberg@lietu.net",
    packages=["taqu", "taqu.aio"],
    keywords="task queue azure service bus",
    python_requires=">=3.5,<4",
    install_requires=["pydantic>=1.4,<2"],
    extras_require={"azure": ["azure-servicebus>=0.50,<1"]},
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    project_urls={
        "Bug Reports": "https://github.com/lietu/taqu/issues",
        "Source": "https://github.com/lietu/taqu/",
    },
)
