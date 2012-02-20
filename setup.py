from setuptools import find_packages
from setuptools import setup

import os


version = '1.0a1'

setup(
    name='plone.app.eventindex',
    version=version,
    description="",
    long_description=open("README.txt").read() + "\n" +
                   open(os.path.join("docs", "HISTORY.txt")).read(),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
    ],
    keywords='plone recurring event index',
    author='Lennart Regebro, Colliberty',
    author_email='regebro@gmail.com',
    url='https://github.com/regebro/plone.app.eventindex',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Zope2',
        'mock',
        'python-dateutil<2.0',
        'setuptools',
        'unittest2',
    ],
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """,
      )
