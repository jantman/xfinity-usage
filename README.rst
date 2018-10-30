xfinity-usage
=============

.. image:: http://www.repostatus.org/badges/latest/active.svg
   :alt: Project Status: Active – The project has reached a stable, usable state and is being actively developed.
   :target: http://www.repostatus.org/#active

Python/selenium script to get Xfinity bandwidth usage from Xfinity MyAccount website. Has an easily-usable
command line entrypoint as well as a usable Python API, and an entrypoint to send usage to Graphite.

This is a little Python script @jantman created that uses the `selenium-python <http://selenium-python.readthedocs.io/>`_
package to log in to your Xfinity account and screen-scrape the data usage. By default the usage is just printed
to STDOUT. You can also use the ``XfinityUsage`` class from other applications or scripts; see the
docstrings on the ``__init__`` and ``run`` methods for information. There are also options to send the data
to a Graphite server.

For the changelog, see `CHANGES.rst in the GitHub project <https://github.com/jantman/xfinity-usage/blob/master/CHANGES.rst>`_.


Requirements
------------

-  Python (tested with 2.7; should work with 3.3+ as well)
-  `selenium <http://selenium-python.readthedocs.io/>`_  Python package
-  One of the supported browsers:

   -  A recent version of PhantomJS installed on your computer; this should be 2.0+, and the script is tested with 2.1.1.
   -  Google Chrome or Chromium and `chromedriver <https://sites.google.com/a/chromium.org/chromedriver/>`_
   -  Firefox and `Geckodriver <https://github.com/mozilla/geckodriver>`_

Installation
------------

    pip install xfinity-usage

Usage
-----

Command Line
++++++++++++

Export your Xfinity username as the ``XFINITY_USER`` environment
variable, your password as the ``XFINITY_PASSWORD`` environment
variable, and run the ``xfinity-usage`` entrypoint. See ``xfinity-usage -h`` and the
top-level docstring in the script for more information.

I'd highly recommend not leaving your username and password hard-coded
anywhere on your system, but the methods for securing credentials are
varied enough that the choice is yours.

Note that this screen-scrapes their site; it's likely to break with a
redesign.

Python API
++++++++++

See the source of the ``xfinity_usage.py`` script, specifically the ``__init__``
and ``run`` methods of the ``XfinityUsage`` class. As a simple example:

.. code-block:: pycon

   >>> import os
   >>> from xfinity_usage.xfinity_usage import XfinityUsage
   >>> u = XfinityUsage(os.environ['XFINITY_USER'], os.environ['XFINITY_PASSWORD'], browser_name='chrome-headless')
   >>> u.run()
   {
       "data_timestamp": 1523913455,
       "units": "GB",
       "used": 224.0,
       "total": 1024.0,
       "raw": {
           "courtesyUsed": 0,
           "courtesyRemaining": 2,
           "courtesyAllowed": 2,
           "inPaidOverage": false,
           "usageMonths": [
               {
                   "policyName": "1 Terabyte Data Plan",
                   "startDate": "10/01/2017",
                   "endDate": "10/31/2017",
                   "homeUsage": 408.0,
                   "allowableUsage": 1024.0,
                   "unitOfMeasure": "GB",
                   "devices": [
                       {
                           "id": "AB:CD:EF:01:23:45",
                           "usage": 301.0
                       },
                       {
                           "id": "12:34:56:78:90:AB",
                           "usage": 107.0
                       }
                   ],
                   "additionalBlocksUsed": 0.0,
                   "additionalCostPerBlock": 10.0,
                   "additionalUnitsPerBlock": 50.0,
                   "additionalIncluded": 0.0,
                   "additionalUsed": 0.0,
                   "additionalPercentUsed": 0.0,
                   "additionalRemaining": 0.0,
                   "billableOverage": 0.0,
                   "overageCharges": 0.0,
                   "overageUsed": 0.0,
                   "currentCreditAmount": 0,
                   "maxCreditAmount": 0,
                   "policy": "limited"
               },
               # 5 additional months removed for brevity
               {
                   "policyName": "1 Terabyte Data Plan",
                   "startDate": "04/01/2018",
                   "endDate": "04/30/2018",
                   "homeUsage": 224.0,
                   "allowableUsage": 1024.0,
                   "unitOfMeasure": "GB",
                   "devices": [
                       {
                           "id": "12:34:56:78:90:AB",
                           "usage": 224.0
                       }
                   ],
                   "additionalBlocksUsed": 0.0,
                   "additionalCostPerBlock": 10.0,
                   "additionalUnitsPerBlock": 50.0,
                   "additionalIncluded": 0.0,
                   "additionalUsed": 0.0,
                   "additionalPercentUsed": 0.0,
                   "additionalRemaining": 0.0,
                   "billableOverage": 0.0,
                   "overageCharges": 0.0,
                   "overageUsed": 0.0,
                   "currentCreditAmount": 0,
                   "maxCreditAmount": 0,
                   "policy": "limited"
               }
           ]
       }
   }

Docker & Kubernetes
+++++++++++++++++++

An example docker implementation of xfinity-usage can be found in `this comcastUsage-for-influxdb repository <https://github.com/billimek/comcastUsage-for-influxdb>`_ which leverages xfinity-usage to emit the data to influxdb in a headless docker container.

A helm chart which leverages the above docker image can also be foind in `this helm charts repository <https://github.com/billimek/billimek-charts/tree/master/comcast>`_.


Note About Reliability
----------------------

In short: xfinity's site isn't terribly reliable. Personally, I run this
script twice an hour via cron, so 48 times a day, every day. I usually
see 1-4 failures a day of all different failure modes - elements missing
from the page, connection resets, blank pages, server-side error
messages, etc. Keep that in mind. My code could probably do more in
terms of error handling and retries, but it's not *that* important to
me.

Rationale
---------

Comcast recently started rolling out a 1TB/month bandwidth cap in my
area. I've gone over my two "courtesy" months, and the overage fees are
pretty insane. I work from home, and sometimes that uses a lot of
bandwidth. I want to know when I'm getting close to my limit; this month
I'm apparently at 75% and only half way through the month, and I have
**no** idea how that happened.

It's entirely abusive and invasive that Comcast is `injecting bandwidth
warnings into my web
traffic <https://www.techdirt.com/articles/20161123/10554936126/comcast-takes-heat-injecting-messages-into-internet-traffic.shtml>`_,
but that's also a pretty awful way of attempting to tell a human
something - especially given how much automated traffic my computer
generates. Moreover,

Xfinity's site has a `Usage Meter <http://www.xfinity.com/usagemeter>`_
(which is the source of this data), but it only shows a progress bar for
the month - no way to find out usage by day or hour to try and figure
out what the cause actually was. Also, even if I visit the usage meter
from my own computer *on Xfinity's network*, using the IP address which
Xfinity assigned to me (and is tracking usage for), I still need to log
in to my account to view the usage. That's a complete pain and seems to
serve only to prevent customers from keeping track of their usage, not
to metion preventing guests or friends from checking usage. Hell,
Xfinity used to have a `desktop app to track
usage <http://usmapp-qa.comcast.net/>`_ but it's been shut down, and a
handy `script that used the same API as the desktop
app <https://github.com/WTFox/comcastUsage>`_ no longer works as a
result. With all of this put together, I'd say Comcast is going to great
lengths to maximize overage fees and minimize customers' insight into
their usage.

In short, I want to be notified of my usage on a regular basis (I get
daily emails with the results of this script), and I also want to be
able to see historical trends (I push the output to Graphite).

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

This package is licensed under the `GNU AGPLv3 <https://www.gnu.org/licenses/agpl-3.0.en.html>`_.

Contributing
------------

For information on contributing, see `.github/CONTRIBUTING.md <https://github.com/jantman/xfinity-usage/blob/master/.github/CONTRIBUTING.md>`_.
