#!/usr/bin/env python
"""
xfinity_usage.py
================

Python script to check your Xfinity data usage. Class can also be used from
other scripts/tools.

(see VERSION constant for version number)

Requirements
------------

- phantomjs >= 2.0 (tested with 2.1.1), Chrome and Chromedriver, or Firefox and
  Geckodriver
- selenium (``pip install selenium``)

Usage
-----

Export your Xfinity username and password as ``XFINITY_USER`` and
``XFINITY_PASSWORD`` environment variables, respectively. See
``xfinity_usage.py -h`` for further information.

Disclaimer
----------

I have no idea what Xfinity's terms of use for their account management website
are, or if they claim to have an issue with automating access. They used to have
a desktop app to check usage, backed by an API (see
https://github.com/WTFox/comcastUsage ), but that's been discontinued. The fact
that they force me to login with my account credentials WHEN CONNECTING FROM
*THEIR* NETWORK, USING THE IP ADDRESS *THEY* ISSUED TO MY ACCOUNT just to check
my usage, pretty clearly shows me that Comcast cares a lot more about extracting
the maximum overage fees from their customers than the "quality of service" that
they claim these bandwidth limits exist for. So... use this at your own risk,
but it seems pretty clear (i.e. discontinuing their "bandwidth meter" desktop
app) that Comcast wants to prevent users from having a clear idea of their
supposed bandwidth usage.

License
-------

Copyright 2017 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
Free for any use provided that patches are submitted back to me.

The latest version of this script can be found at:
<https://github.com/jantman/xfinity-usage>

CHANGELOG (see VERSION constant for version number)
---------------------------------------------------

1.0.0 2017-11-06 Jason Antman <jason@jasonantman.com>
  - Added VERSION constant and began tagging git repo for releases
  - Updated User-Agent string to latest chrome, with "xfinity-usage/VERSION"
    appended.
  - Exposed ``browser_name`` parameter on class and as command line argument to
    allow use with browsers other than phantomjs.
  - Added headless chromedriver browser option.
  - Set window size to 1024x768 for all browser types.

2017-06-30 Jeff Billimek <jeff@billimek.com>:
  - making more friendly for invocation as a class

2017-06-22 Jason Antman <jason@jasonantman.com>:
  - clarify PhantomJS requirement of 2.x (2.1.1 recommended)

2017-06-22 Jason Antman <jason@jasonantman.com>:
  - remove superfluous print statement introduced in last commit

2017-06-21 Jason Antman <jason@jasonantman.com>:
  - update for My Account redesign

2017-04-20 Jason Antman <jason@jasonantman.com>:
  - ensure we quit browser before exiting, to prevent orphaned phantomjs procs

2017-04-18 Jason Antman <jason@jasonantman.com>:
  - make more reliable by not saving or loading cookies

2017-04-18 Jason Antman <jason@jasonantman.com>:
  - more complicated wait logic to handle redirects and long page loads

2017-04-17 Jason Antman <jason@jasonantman.com>:
  - update for difference in form after "Remember Me"

2017-04-16 Jason Antman <jason@jasonantman.com>:
  - initial version of script
"""

import sys
import os
import argparse
import logging
import json
import codecs
import time
import re

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

VERSION = '1.0.0'

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
            self.browser.quit()
            raise

    def do_login(self):
        logger.info('Logging in (%s)', self.browser.current_url)
        self.wait_for_page_load()
        self.do_screenshot()
        try:
            meter = self.browser.find_element_by_xpath(
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
            except:
                logger.critical('Unable to find username input box!', exc_info=True)
                self.do_screenshot()
            try:
                rem_me = self.browser.find_element_by_id('remember_me')
                if not rem_me.is_selected():
                    logger.debug('Clicking "Remember Me"')
                    rem_me.click()
            except:
                self.error_screenshot()
                logger.warning('Unable to find Remember Me button!',
                               exc_info=True)
        try:
            p = self.browser.find_element_by_id('passwd')
        except:
            logger.critical('Unable to find passwd input box!', exc_info=True)
            self.error_screenshot()
            raise RuntimeError("Unable to find passwd input.")
        try:
            btn = self.browser.find_element_by_id('sign_in')
        except:
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
                '//div[@class="usage-info__monthlyInfo"]'
            )
            logger.debug('Found monthly usage div')
        except Exception:
            logger.critical('Unable to find monthly usage div on page',
                            exc_info=True)
            self.error_screenshot()
            raise RuntimeError('Unable to find monthly usage div.')
        t = meter.find_element_by_xpath(
            '//span'
            '[@ng-bind-html="usage.details.userMessage.monthlyUsageState"]'
        )
        logger.debug('Usage meter text: %s', t.text)
        m = re.search(
            r'(\d+)([A-Za-z]+) remaining of (\d+)([A-Za-z]+) monthly plan',
            t.text
        )
        if m is None:
            raise RuntimeError('Cannot parse string: %s' % t.text)
        remain = float(m.group(1))
        remain_unit = m.group(2)
        total = float(m.group(3))
        total_unit = m.group(4)
        if remain_unit != total_unit:
            raise RuntimeError(
                'Data remaining unit (%s) not the same as total unit (%s)' % (
                    remain_unit, total_unit
                )
            )
        used = total - remain
        return {'units': remain_unit, 'used': used, 'total': total}

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
                    b=browser_name
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


def parse_args(argv):
    """
    parse command line arguments
    """
    p = argparse.ArgumentParser(description='Check Xfinity data usage')
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

if __name__ == "__main__":
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
