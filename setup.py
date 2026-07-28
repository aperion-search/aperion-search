# SPDX-License-Identifier: AGPL-3.0-or-later
"""Installer for aperion package."""

from setuptools import setup, find_packages
import os

# Read version directly from file
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'aperion', 'version.py')
    with open(version_file, 'r') as f:
        for line in f:
            if line.startswith('VERSION_TAG'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '1.0.0'

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = [ l.strip() for l in f.readlines()]

setup(
    name='aperion',
    python_requires=">=3.8",
    version=get_version(),
    description="A privacy-respecting, hackable metasearch engine",
    long_description=long_description,
    url='https://docs.aperion.org/',
    project_urls={
        "Code": 'https://github.com/Aperion-Search/Aperion-Search',
        "Issue tracker": 'https://github.com/Aperion-Search/Aperion-Search/issues/'
    },
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        'License :: OSI Approved :: GNU Affero General Public License v3'
    ],
    keywords='metasearch searchengine search web http',
    author='aperion dev team',
    author_email='contact@aperion.org',
    license='GNU Affero General Public License',
    packages=find_packages(
        include=[
            'aperion', 'aperion.*', 'aperion.*.*', 'aperion.*.*.*',
        ]
    ),
    install_requires=requirements,
    extras_require={
        'test': requirements
    },
    entry_points={
        'console_scripts': [
            'aperion-run = aperion.webapp:run',
            'aperion-checker = aperion.search.checker.__main__:main'
        ]
    },
    package_data={
        'aperion': [
            'settings.yml',
            '*.toml',
            '*.msg',
            'search/checker/scheduler.lua',
            'data/*.json',
            'data/*.txt',
            'data/*.ftz',
            'favicons/*.toml',
            'infopage/*/*',
            'static/themes/simple/css/*',
            'static/themes/simple/css/*/*',
            'static/themes/simple/img/*',
            'static/themes/simple/js/*',
            'templates/*/*',
            'templates/*/*/*',
            'translations/*',
            'translations/*/*',
            'translations/*/*/*',
        ],
    },
)
