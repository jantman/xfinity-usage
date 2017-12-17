"""
The latest version of this package is available at:
<http://github.com/jantman/xfinity-usage>

##################################################################################
Copyright 2017 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

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

from xfinity_usage.xfinity_usage import XfinityUsage


class TestXfinityUsage(object):

    def test_usage_url(self):
        """
        We don't have real unit tests yet. For now, add one to just make sure
        the class can be imported
        """
        expected = 'https://customer.xfinity.com/#/devices'
        assert XfinityUsage.USAGE_URL == expected
