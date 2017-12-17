Changelog
=========

2.0.0 (2017-12-17)
------------------

  - Package as a real Python package and upload to PyPI; this changes the layout
    of the repository, but if you want to use the previous script unmodified you
    can now do so via ``pip install xfinity-usage`` instead of having to git clone.
  - Add support for unit tests, but no real tests yet

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
