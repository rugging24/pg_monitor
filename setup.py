#!/usr/bin/python 

from setuptools import setup

setup(name='pg_monitor',
      version='1.0',
      description='PostgreSQL monitoring checks',
      url='https://github.com/rugging24/pg_monitor',
      author='Olakunle Olaniyi',
      author_email='rugging24@gmail.com',
      license='PostgreSQL License',
      packages=['pg_monitor'],
      install_requires=[
          'psycopg2',
      ],
      zip_safe=False)
