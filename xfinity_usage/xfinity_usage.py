#!/usr/bin/env python
"""
xfinity-usage Python package
============================

Python script to check your Xfinity data usage. Class can also be used from
other scripts/tools.

The latest version of this script can be found at:
<https://github.com/jantman/xfinity-usage>

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
"""

import sys
import os
import argparse
import logging
import json
import codecs
import time
import re
from datetime import datetime
import socket

from .version import VERSION, PROJECT_URL

try:
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.desired_capabilities import \
        DesiredCapabilities
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    sys.stderr.write("Error importing selenium - 'pip install selenium'\n")
    raise SystemExit(1)

FORMAT = "[%(asctime)s %(levelname)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger = logging.getLogger()

# suppress selenium DEBUG logging
selenium_log = logging.getLogger('selenium')
selenium_log.setLevel(logging.INFO)
selenium_log.propagate = True


class XfinityUsage(object):
    """Class to screen-scrape Xfinity site for usage information."""

    USAGE_URL = 'https://customer.xfinity.com/#/devices'

    def __init__(self, username, password, debug=False,
                 cookie_file='cookies.json', browser_name='phantomjs'):
        """
        Initialize class.

        :param username: Xfinity account username
        :type username: str
        :param password: Xfinity account password
        :type password: str
        :param debug: If true, screenshot all pages
        :type debug: bool
        :param cookie_file: file to save cookies in
        :type cookie_file: str
        :param browser_name: Name of the browser to use. Can be one of
        :type browser_name: str
        """
        self._screenshot = debug
        if debug:
            set_log_debug()
        if username is None or password is None:
            raise RuntimeError("Username and password cannot be None")
        self.username = username
        self.password = password
        self.browser_name = browser_name
        self.browser = None
        self._screenshot_num = 1
        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36' \
                          ' (KHTML, like Gecko) Chrome/62.0.3202.62 ' \
                          'xfinity-usage/%s' % VERSION
        self.cookie_file = cookie_file
        logger.debug('Getting browser instance...')

    def run(self):
        """
        Check usage. Returns the return value of ``get_usage()``.
        """
        logger.debug('Getting page...')
        try:
            self.browser = self.get_browser()
            self.get_usage_page()
            res = self.get_usage()
            self.browser.quit()
            return res
        except Exception:
            if self.browser is not None:
                self.browser.quit()
            raise

    def do_login(self):
        logger.info('Logging in (%s)', self.browser.current_url)
        self.wait_for_page_load()
        self.do_screenshot()
        try:
            self.browser.find_element_by_xpath(
                '//div[@data-component="usage-meter"]'
            )
            logger.info('Found usage meter on page')
            return True
        except Exception:
            pass
        if self.username not in self.browser.page_source:
            try:
                u = self.browser.find_element_by_id('user')
                u.clear()
                u.send_keys(self.username)
            except Exception:
                logger.critical(
                    'Unable to find username input box!', exc_info=True
                )
                self.do_screenshot()
            try:
                rem_me = self.browser.find_element_by_id('remember_me')
                if not rem_me.is_selected():
                    logger.debug('Clicking "Remember Me"')
                    # because of layering issues, for chrome-headless we need to
                    # click the containing span instead of the checkbox itself.
                    self.browser.find_element_by_id(
                        'remember_me_checkbox'
                    ).click()
            except Exception:
                self.error_screenshot()
                logger.warning('Unable to find Remember Me button!',
                               exc_info=True)
        try:
            p = self.browser.find_element_by_id('passwd')
        except Exception:
            logger.critical('Unable to find passwd input box!', exc_info=True)
            self.error_screenshot()
            raise RuntimeError("Unable to find passwd input.")
        try:
            btn = self.browser.find_element_by_id('sign_in')
        except Exception:
            logger.critical('Unable to find Sign In button!', exc_info=True)
            self.error_screenshot()
            raise RuntimeError("Unable to find Sign In button.")
        p.clear()
        p.send_keys(self.password)
        logger.debug('Clicking Sign In button')
        oldurl = self.browser.current_url
        self.do_screenshot()
        btn.click()
        self.do_screenshot()
        count = 0
        while self.browser.current_url == oldurl:
            self.do_screenshot()
            count += 1
            if count > 10:
                self.error_screenshot()
                raise RuntimeError("Login button clicked but no redirect")
            logger.info('Sleeping 1s for redirect after login button click')
            time.sleep(1)
        self.wait_for_page_load()
        self.do_screenshot()

    def get_usage_page(self, count=0):
        """Get the usage page"""
        self.get(self.USAGE_URL)
        self.wait_for_page_load()
        self.do_screenshot()
        # see if we have the sign_in button; if not, we're logged in
        logged_in = True
        try:
            self.wait_by(By.ID, 'sign_in')
            logger.info('Not logged in; logging in now')
            logged_in = False
        except Exception:
            pass
        self.do_screenshot()
        if not logged_in:
            if count > 5:
                self.error_screenshot()
                raise RuntimeError("Tried 5 times to log in; all failed.")
            try:
                logger.info('Trying to login...')
                self.do_login()
                self.get_usage_page(count=(count + 1))
            except Exception:
                logger.warning('Exception while logging in', exc_info=True)
        logger.info('Sleeping 5s...')
        time.sleep(5)  # unfortunately, seems necessary
        self.wait_for_page_load()
        self.do_screenshot()
        if '<span class="polaris-greeting">' not in self.browser.page_source:
            logger.info('<span class="polaris-greeting"> not in page source;'
                        'login may have failed.')
        self.do_screenshot()

    def get_usage(self):
        """
        Get the actual usage from the page

        Returned dict has 3 keys: ``used`` (float) used data, ``total`` (float)
        total data for plan, ``units`` (str) unit descriptor ("GB").

        :returns: dict describing usage
        :rtype: dict
        """
        self.do_screenshot()
        try:
            meter = self.browser.find_element_by_xpath(
                '//*'
                '[@ng-bind-html="usage.details.userMessage.monthlyUsageState"]'
            )
            logger.debug('Found monthly usage divs')
        except Exception:
            logger.critical('Unable to find monthly usage div on page',
                            exc_info=True)
            self.error_screenshot()
            raise RuntimeError('Unable to find monthly usage div.')
        logger.debug('Usage meter text: %s', meter.text)
        try:
            used_xpath = '//div[@usage-data="usage.details.usageData"]' \
                         '//tr[last()]/td[1]'
            self.wait_by(By.XPATH, used_xpath)
            used_td = self.browser.find_element_by_xpath(used_xpath)
            logger.debug('Found current Total Monthly Usage table cell')
            used_value = used_td.get_attribute('innerHTML')
        except Exception:
            logger.critical('Unable to find current Total Monthly Usage '
                            'table cell', exc_info=True)
            self.error_screenshot()
            raise RuntimeError('Unable to find current Total Monthly Usage '
                               'table cell.')
        logger.debug('Montly Usage TD: %s', used_value)
        m = re.search(
            r'(\d+)([A-Za-z]+) remaining of (\d+)([A-Za-z]+) monthly plan',
            meter.text
        )
        if m is None:
            raise RuntimeError('Cannot parse string: %s' % meter.text)
        d = re.search(r'(\d+)\s*([A-Za-z]+)', used_value)
        if d is None:
            raise RuntimeError('Cannot parse string: %s' % used_value)
        used = float(d.group(1))
        used_unit = d.group(2)
        total = float(m.group(3))
        total_unit = m.group(4)
        if used_unit != total_unit:
            raise RuntimeError(
                'Data remaining unit (%s) not the same as total unit (%s)' % (
                    used_unit, total_unit
                )
            )
        return {'units': used_unit, 'used': used, 'total': total}

    def do_screenshot(self):
        """take a debug screenshot"""
        if not self._screenshot:
            return
        fname = os.path.join(
            os.getcwd(), '{n}.png'.format(n=self._screenshot_num)
        )
        self.browser.get_screenshot_as_file(fname)
        logger.debug(
            "Screenshot: {f} of: {s}".format(
                f=fname,
                s=self.browser.current_url
            )
        )
        self._screenshot_num += 1

    def error_screenshot(self, fname=None):
        if fname is None:
            fname = os.path.join(os.getcwd(), 'webdriver_fail.png')
        self.browser.get_screenshot_as_file(fname)
        logger.error("Screenshot saved to: {s}".format(s=fname))
        logger.error("Page title: %s", self.browser.title)
        html_path = os.path.join(os.getcwd(), 'webdriver_fail.html')
        source = self.browser.execute_script(
            "return document.getElementsByTagName('html')[0].innerHTML"
        )
        with codecs.open(html_path, 'w', 'utf-8') as fh:
            fh.write(source)
        logger.error('Page source saved to: %s', html_path)

    def get(self, url):
        """logging wrapper around browser.get"""
        logger.info('GET %s', url)

        self.browser.get(url)
        for x in range(0, 5):
            try:
                WebDriverWait(self.browser, 15).until(
                    lambda x: self.browser.current_url != 'about:blank'
                )
                break
            except Exception:
                logger.warning('GET %s failed; trying again', url)
            self.browser.get(url)
            time.sleep(2)
        else:
            self.error_screenshot()
            raise RuntimeError('GET %s failed' % url)

    def get_browser(self):
        """get a webdriver browser instance """
        if self.browser_name == 'firefox':
            logger.debug("getting Firefox browser (local)")
            if 'DISPLAY' not in os.environ:
                logger.debug("exporting DISPLAY=:0")
                os.environ['DISPLAY'] = ":0"
            browser = webdriver.Firefox()
        elif self.browser_name == 'chrome':
            logger.debug("getting Chrome browser (local)")
            browser = webdriver.Chrome()
        elif self.browser_name == 'chrome-headless':
            logger.debug('getting Chrome browser (local) with --headless')
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            browser = webdriver.Chrome(chrome_options=chrome_options)
        elif self.browser_name == 'phantomjs':
            logger.debug("getting PhantomJS browser (local)")
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = self.user_agent
            args = [
                '--ssl-protocol=any',
                '--ignore-ssl-errors=true',
                '--web-security=false'
            ]
            browser = webdriver.PhantomJS(
                desired_capabilities=dcap, service_args=args
            )
        else:
            raise SystemExit(
                "ERROR: browser type must be one of 'firefox', 'chrome', "
                "'phantomjs', or 'chrome-headless' not '{b}'".format(
                    b=self.browser_name
                )
            )
        browser.set_window_size(1024, 768)
        logger.debug("returning browser")
        return browser

    def doc_readystate_is_complete(self, _):
        """ return true if document is ready/complete, false otherwise """
        result_str = self.browser.execute_script("return document.readyState")
        if result_str == "complete":
            return True
        return False

    def wait_for_page_load(self, timeout=20):
        """
        Function to wait for page load.

        timeout is in seconds
        """
        self.wait_for_ajax_load(timeout=timeout)
        count = 0
        while len(self.browser.page_source) < 30:
            if count > 20:
                self.error_screenshot()
                raise RuntimeError("Waited 20s for page source to be more "
                                   "than 30 bytes, but still too small...")
            count += 1
            logger.debug('Page source is only %d bytes; sleeping',
                         len(self.browser.page_source))
            time.sleep(1)

    def wait_for_ajax_load(self, timeout=20):
        """
        Function to wait for an ajax event to finish and trigger page load.

        Pieced together from
        http://stackoverflow.com/a/15791319

        timeout is in seconds
        """
        WebDriverWait(self.browser, timeout).until(
            self.doc_readystate_is_complete
        )
        return True

    def wait_by(self, _by, arg, timeout=20):
        """
        Wait for an element By something.
        """
        WebDriverWait(self.browser, timeout).until(
            EC.presence_of_element_located((_by, arg))
        )

    def load_cookies(self, cookie_file):
        """
        Load cookies from a JSON cookie file on disk. This file is not the
        format used natively by PhantomJS, but rather the JSON-serialized
        representation of the dict returned by
        :py:meth:`selenium.webdriver.remote.webdriver.WebDriver.get_cookies`.

        Cookies are loaded via
        :py:meth:`selenium.webdriver.remote.webdriver.WebDriver.add_cookie`

        :param cookie_file: path to the cookie file on disk
        :type cookie_file: str
        """
        if not os.path.exists(cookie_file):
            logger.warning('Cookie file does not exist: %s', cookie_file)
            return
        logger.info('Loading cookies from: %s', cookie_file)
        with open(cookie_file, 'r') as fh:
            cookies = json.loads(fh.read())
        count = 0
        for c in cookies:
            try:
                self.browser.add_cookie(c)
                count += 1
            except Exception as ex:
                logger.info('Error loading cookie %s: %s', c, ex)
        logger.debug('Loaded %d of %d cookies', count, len(cookies))

    def save_cookies(self, cookie_file):
        """
        Save cookies to a JSON cookie file on disk. This file is not the
        format used natively by PhantomJS, but rather the JSON-serialized
        representation of the dict returned by
        :py:meth:`selenium.webdriver.remote.webdriver.WebDriver.get_cookies`.

        :param cookie_file: path to the cookie file on disk
        :type cookie_file: str
        """
        cookies = self.browser.get_cookies()
        raw = json.dumps(cookies)
        with open(cookie_file, 'w') as fh:
            fh.write(raw)
        logger.info('Wrote %d cookies to: %s', len(cookies), cookie_file)


class GraphiteSender(object):

    def __init__(self, host, port, prefix='xfinity'):
        self.host = host
        self.port = port
        self.prefix = prefix
        logger.info('Sending graphite data to %s:%s', host, port)

    def _graphite_send(self, send_str):
        """
        Send data to graphite

        :param send_str: data string to send
        :type send_str: str
        """
        logger.debug('Opening socket connection to %s:%s', self.host, self.port)
        sock = socket.create_connection((self.host, self.port), 10)
        logger.debug('Sending data: "%s"', send_str)
        if sys.version_info[0] > 2:
            sock.sendall(send_str.encode('utf-8'))
        else:
            sock.sendall(send_str)
        logger.info('Data sent to Graphite')
        sock.close()

    def _clean_name(self, metric_name):
        """
        Return a graphite-safe metric name.

        :param metric_name: original metric name
        :type metric_name: str
        :return: graphite-safe metric name
        :rtype: str
        """
        metric_name = metric_name.lower()
        newk = re.sub(r'[^A-Za-z0-9_-]', '_', metric_name)
        if newk != metric_name:
            logger.debug('Cleaned metric name from "%s" to "%s"',
                         metric_name, newk)
        return newk

    def send_data(self, data):
        """
        Send data to Graphite.

        :param data: list of data dicts
        :type data: list
        """
        send_str = ''
        for d in data:
            ts = time.mktime(d['datetime'].timetuple())
            for k in sorted(d.keys()):
                if k == 'datetime':
                    continue
                send_str += "%s %s %d\n" % (
                    '%s.%s' % (self.prefix, self._clean_name(k)),
                    d[k],
                    ts
                )
        self._graphite_send(send_str)


def parse_args(argv):
    """
    parse command line arguments
    """
    p = argparse.ArgumentParser(
        description='Check Xfinity data usage; see <%s> for more '
                    'information' % PROJECT_URL, prog='xfinity-usage'
    )
    p.add_argument('-V', '--version', action='version',
                   version='xfinity-usage %s <%s>' % (VERSION, PROJECT_URL))
    p.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                   help='verbose output. specify twice for debug-level output.')
    p.add_argument('-c', '--cookie-file', dest='cookie_file', action='store',
                   type=str,
                   default=os.path.realpath('xfinity_usage_cookies.json'),
                   help='File to save cookies in')
    browsers = ['phantomjs', 'firefox', 'chrome', 'chrome-headless']
    p.add_argument('-b', '--browser', dest='browser_name', type=str,
                   default='phantomjs', choices=browsers,
                   help='Browser name/type to use')
    p.add_argument('-j', '--json', dest='json', action='store_true',
                   default=False, help='output JSON')
    p.add_argument('-g', '--graphite', action='store_true', default=False,
                   help='send metrics to graphite', dest='graphite')
    p.add_argument('-H', '--graphite-host', action='store', type=str,
                   dest='graphite_host', default='127.0.0.1',
                   help='Graphite host to send to (default: 127.0.0.1)')
    p.add_argument('-P', '--graphite-port', action='store', type=int,
                   dest='graphite_port', default='2003',
                   help='Graphite port to send to (default: 2003)')
    p.add_argument('-p', '--graphite-prefix', action='store', type=str,
                   dest='graphite_prefix', default='xfinity',
                   help='graphite metric prefix (default: xfinity)')
    args = p.parse_args(argv)
    return args


def set_log_info():
    """set logger level to INFO"""
    set_log_level_format(logging.INFO,
                         '%(asctime)s %(levelname)s:%(name)s:%(message)s')


def set_log_debug():
    """set logger level to DEBUG, and debug-level output format"""
    set_log_level_format(
        logging.DEBUG,
        "%(asctime)s [%(levelname)s %(filename)s:%(lineno)s - "
        "%(name)s.%(funcName)s() ] %(message)s"
    )


def set_log_level_format(level, format):
    """
    Set logger level and format.

    :param level: logging level; see the :py:mod:`logging` constants.
    :type level: int
    :param format: logging formatter format string
    :type format: str
    """
    formatter = logging.Formatter(fmt=format)
    logger.handlers[0].setFormatter(formatter)
    logger.setLevel(level)


def main():
    args = parse_args(sys.argv[1:])

    # set logging level
    debug = False
    if args.verbose > 1:
        set_log_debug()
        debug = True
    elif args.verbose == 1:
        set_log_info()

    if 'XFINITY_USER' not in os.environ:
        raise SystemExit("ERROR: please export your Xfinity username as the "
                         "XFINITY_USER environment variable.")
    if 'XFINITY_PASSWORD' not in os.environ:
        raise SystemExit("ERROR: please export your Xfinity password as the "
                         "XFINITY_PASSWORD environment variable.")
    script = XfinityUsage(
        os.environ['XFINITY_USER'],
        os.environ['XFINITY_PASSWORD'],
        debug=debug,
        cookie_file=args.cookie_file,
        browser_name=args.browser_name
    )
    res = script.run()
    if args.json:
        print(json.dumps(res))
        raise SystemExit(0)
    print("Used %d of %d %s this month." % (
        res['used'], res['total'], res['units']
    ))
    if args.graphite:
        # send to graphite
        sender = GraphiteSender(
            args.graphite_host, args.graphite_port, prefix=args.graphite_prefix
        )
        sender.send_data([{
            'datetime': datetime.now(),
            'used_%s' % res['units']: res['used'],
            'total_%s' % res['units']: res['total']
        }])


if __name__ == "__main__":
    main()
