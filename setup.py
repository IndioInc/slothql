from distutils.core import setup
from setuptools import find_packages

VERSION = '0.1.0a0'

setup(
    name='slothql',
    version=VERSION,
    description='The async GraphQL framework.',
    long_description=open('README.rst').read(),

    author='Karol Gruszczyk',
    author_email='karol.gruszczyk@gmail.com',

    packages=find_packages(exclude=['*.tests*']),

    url='https://github.com/IndioInc/slothql/',
    keywords='graphql framework django async aiohttp relay graphene',

    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='~=3.6',

    install_requires=[
        'graphql-core>=2.0,<3',
    ],
    platforms='any',
    include_package_data=True,
)
