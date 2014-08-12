# -*- coding: utf-8 -*-

###
#   Copyright (C) 2013
#   Fraunhofer Institute for Open Communication Systems (FOKUS)
#   Competence Center NETwork research (NET), St. Augustin, GERMANY
#       Alton MacDonald <alton.kenneth.macdonald@fokus.fraunhofer.de>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
###

import os, sys
import multiprocessing

from setuptools import setup, find_packages
from setuptools.command.install import install

class custom_install(install):
    def run(self):
        from subprocess import call
        install.run(self)
        call(['/usr/sbin/update-rc.d', 'osmocom-oohmi', 'defaults'])

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_mako',
    'pyramid_debugtoolbar',
    'pyramid_exclog',
    'waitress',
    'nose',
    'coverage'
    ]
    
data_files=[('/etc/openbsc', ['production.ini']),
            ('/etc/init.d', ['osmocom-oohmi'])]

setup(name='osmo_oohmi',
      version='0.0',
      description='osmo_oohmi',
      long_description=README + '\n\n' + CHANGES,
      license='AGPLv3',
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        ],
      author='Alton MacDonald',
      author_email='alton.kenneth.macdonald@fokus.fraunhofer.de',
      url='http://git.osmocom.org/python/osmo-oohmi/',
      keywords='openbsc web pyramid pylons',
      packages=find_packages(),
      data_files=data_files,
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="nose.collector",
      entry_points="""\
      [paste.app_factory]
      main = hlr_mgmt:main
      """,
      cmdclass={'install': custom_install}
      )
