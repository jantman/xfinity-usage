Changelog
=========

3.0.4 (2020-09-15)
------------------
- Made new firefox-headless browser the new default browser (since it works)
- Added options to firefox-headless to avoid bot checks when getting usage from xfinity's site
- Cleaned up -b argument help message and choices

3.0.3 (2018-10-30)
------------------

- Updated README with information about usage in Docker & kubernetes

3.0.2 (2018-10-21)
------------------

- New maintainer: @billimek

3.0.1 (2018-09-02)
------------------

- I'm canceling my Xfinity service and switching to AT&T Fiber. Updated README stating that I'm looking for a new maintainer for the project.

3.0.0 (2018-04-18)
-----------------

- Get raw JSON data from the ``https://customer.xfinity.com/apis/services/internet/usage`` endpoint.
- If the above succeeds, use this for data source instead of screen-scraping the page.
- Add raw JSON data from above to output in "raw" key.
- Add scrape time to JSON output in "data_timestamp" key.

2.0.2 (2018-02-12)
------------------

- Fix ``run()`` method exception handler calling ``.quit()`` on missing ``browser`` attribute when ``get_browser()`` raises an exception, causing a confusing traceback.
- Fix issue where ``remember_me`` checkbox is not clickable using Chrome Headless, resulting in "Element is not clickable" / "Other element would receive the click" error.

2.0.1 (2017-12-18)
------------------

- Update README.rst with example of Python usage.
- Fix CHANGELOG formatting

2.0.0 (2017-12-17)
------------------

- Package as a real Python package and upload to PyPI; this changes the layout
  of the repository, but if you want to use the previous script unmodified you
  can now do so via ``pip install xfinity-usage`` instead of having to git clone.
- Add support for unit tests, but no real tests yet
- Add support for optionally sending metrics to a `Graphite <https://graphiteapp.org/>`_ instance.

1.2.0 (2017-12-04)
------------------

- Update for redesign that removed ``ng-if="device.usage"`` element.

1.1.0 (2017-11-30)
------------------

- Merge PR #6 from ericzinnikas to handle reporting used amount even if it is over data cap.

1.0.0 (2017-11-06)
------------------

- Added VERSION constant and began tagging git repo for releases
- Updated User-Agent string to latest chrome, with "xfinity-usage/VERSION"
  appended.
- Exposed ``browser_name`` parameter on class and as command line argument to
  allow use with browsers other than phantomjs.
- Added headless chromedriver browser option.
- Set window size to 1024x768 for all browser types.


2017-06-30
----------

- making more friendly for invocation as a class

2017-06-22
----------

- clarify PhantomJS requirement of 2.x (2.1.1 recommended)

2017-06-22
----------

- remove superfluous print statement introduced in last commit

2017-06-21
----------

- update for My Account redesign

2017-04-20
----------

- ensure we quit browser before exiting, to prevent orphaned phantomjs procs

2017-04-18
----------

- make more reliable by not saving or loading cookies

2017-04-18
----------

- more complicated wait logic to handle redirects and long page loads

2017-04-17
----------

- update for difference in form after "Remember Me"

2017-04-16
----------

- initial version of script
