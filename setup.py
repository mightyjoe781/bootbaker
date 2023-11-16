# setup.py
from setuptools import setup, find_packages

setup(
    name='BootBaker',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'psutils',
    ],
    entry_points={
        'console_scripts': [
            'bootbaker = src.cli:main',
        ],
    },
)