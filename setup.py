#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'PyQt5',
]

setup(
    name='qt_style_sheet_inspector',
    version='0.1.0',
    description="A inspector widget to view and modify style sheet of a Qt app in runtime.",
    long_description=readme + '\n\n' + history,
    author="Rafael Bertoldi",
    author_email='tochaman@gmail.com',
    url='https://github.com/ESSS/qt_style_sheet_inspector',
    packages=[
        'qt_style_sheet_inspector',
    ],
    package_dir={'qt_style_sheet_inspector':
                 'qt_style_sheet_inspector'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='qt_style_sheet_inspector',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=[],
)
