"""
The latest version of this package is available at:
<http://github.com/jantman/xfinity-usage>

##################################################################################
Copyright 2017 Jason Antman <jason@jasonantman.com>

    This file is part of xfinity-usage, also known as xfinity-usage.

    xfinity-usage is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    xfinity-usage is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with xfinity-usage.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
##################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/xfinity-usage> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
##################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
##################################################################################
"""

from setuptools import setup, find_packages
from xfinity_usage.version import VERSION, PROJECT_URL

with open('README.rst') as file:
    long_description = file.read()

requires = [
    'selenium'
]

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: GNU Affero General Public License v3 or '
    'later (AGPLv3+)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Topic :: Home Automation',
    'Topic :: Internet',
    'Topic :: System :: Monitoring',
    'Topic :: System :: Networking :: Monitoring',
]

setup(
    name='xfinity-usage',
    version=VERSION,
    author='Jason Antman',
    author_email='jason@jasonantman.com',
    packages=find_packages(),
    url=PROJECT_URL,
    description='Python/selenium script to get Xfinity bandwidth usage from '
                'Xfinity MyAccount website.',
    long_description=long_description,
    install_requires=requires,
    keywords="comcast xfinity usage data meter bandwidth",
    classifiers=classifiers,
    entry_points="""
    [console_scripts]
    xfinity-usage = xfinity_usage.xfinity_usage:main
    """
)
