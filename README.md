# xfinity-usage

Python/selenium script to get Xfinity bandwidth usage

This is a little Python script I whipped up that uses [PhantomJS](http://phantomjs.org/) via the [selenium-python](http://selenium-python.readthedocs.io/) package to log in to your Xfinity account and screen-scrape the data usage. By default the usage is just printed to STDOUT. You can also use the ``XfinityUsage`` class from other applications or scripts; see the docstrings on the ``__init__`` and ``run`` methods for information.

## Requirements

* Python (tested with 2.7; should work with 3.3+ as well)
* ``selenium`` Python package (``pip install selenium``)
* A recent version of PhantomJS installed on your computer; this should be 2.0+, and the script is tested with 2.1.1.

## Usage

Export your Xfinity username as the ``XFINITY_USER`` environment variable, your password as the ``XFINITY_PASSWORD`` environment variable, and run the script. See ``xfinity_usage.py -h`` and the top-level docstring in the script for more information.

I'd highly recommend not leaving your username and password hard-coded anywhere on your system, but the methods for securing credentials are varied enough that the choice is yours.

Note that this screen-scrapes their site; it's likely to break with a redesign.

## Rationale

Comcast recently started rolling out a 1TB/month bandwidth cap in my area. I've gone over my two "courtesy" months, and the overage fees are pretty insane. I work from home, and sometimes that uses a lot of bandwidth. I want to know when I'm getting close to my limit; this month I'm apparently at 75% and only half way through the month, and I have **no** idea how that happened.

It's entirely abusive and invasive that Comcast is [injecting bandwidth warnings into my web traffic](https://www.techdirt.com/articles/20161123/10554936126/comcast-takes-heat-injecting-messages-into-internet-traffic.shtml), but that's also a pretty awful way of attempting to tell a human something - especially given how much automated traffic my computer generates. Moreover,

Xfinity's site has a [Usage Meter](http://www.xfinity.com/usagemeter) (which is the source of this data), but it only shows a progress bar for the month - no way to find out usage by day or hour to try and figure out what the cause actually was. Also, even if I visit the usage meter from my own computer *on Xfinity's network*, using the IP address which Xfinity assigned to me (and is tracking usage for), I still need to log in to my account to view the usage. That's a complete pain and seems to serve only to prevent customers from keeping track of their usage, not to metion preventing guests or friends from checking usage. Hell, Xfinity used to have a [desktop app to track usage](http://usmapp-qa.comcast.net/) but it's been shut down, and a handy [script that used the same API as the desktop app](https://github.com/WTFox/comcastUsage) no longer works as a result. With all of this put together, I'd say Comcast is going to great lengths to maximize overage fees and minimize customers' insight into their usage.

In short, I want to be notified of my usage on a regular basis (I get daily emails with the results of this script), and I also want to be able to see historical trends (I push the output to Graphite).

## Disclaimer

I don't recall seeing anything in Xfinity's terms about screen-scraping, but please check your terms of service and other appropriate legal agreements before using this.
