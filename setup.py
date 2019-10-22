#!/usr/bin/env python

from setuptools import setup

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    name="pipe",
    py_modules=["pipe"],
    version="1.5.0",
    description="Module enablig a sh like infix syntax (using pipes)",
    author="Julien Palard",
    author_email="julien@palard.fr",
    url="https://github.com/JulienPalard/Pipe",
    download_url="https://github.com/JulienPalard/Pipe/tarball/master",
    long_description=readme,
    long_description_content_type="text/markdown; charset=UTF-8",
    license="MIT license",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
