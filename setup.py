#!/usr/bin/python 

from setuptools import setup

def readme():
    with open('README.txt') as f:
        return f.read()

setup(name='pg_monitor',
      version='1.5.7',
      description='PostgreSQL monitoring checks',
      long_description=readme(),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking :: Monitoring',
      ],
      url='https://github.com/rugging24/pg_monitor',
      author='Olakunle Olaniyi',
      author_email='rugging24@gmail.com',
      license='PostgreSQL License',
      packages=['pg_monitor'],
      install_requires=[
          'psycopg2',
      ],
      scripts=['bin/pg_monitor'],
      include_package_data=True,
      zip_safe=False)
