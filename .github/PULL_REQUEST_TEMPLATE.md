__IMPORTANT:__ Please take note of the below checklist, especially the first two items.

# Pull Request Checklist

- [ ] All pull requests must include the Contributor License Agreement (see below).
- [ ] Code should conform to the following:
    - [ ] pep8 compliant with some exceptions (see pytest.ini)
    - [ ] Complete, correctly-formatted documentation for all classes, functions and methods.
    - [ ] Code works under Python 2.7 and Python 3.3+
    - [ ] **Commit messages** should be meaningful, and reference the Issue number
      if you're working on a GitHub issue (i.e. "issue #x - <message>"). Please
      refrain from using the "fixes #x" notation unless you are *sure* that the
      the issue is fixed in that commit.
    - [ ] Git history is fully intact; please do not squash or rewrite history.
- [ ] If you're sure your code works, adding a relevant entry to ``CHANGES.rst`` and
  bumping the version number in ``xfinity_usage/version.py`` will get it merged and
  released faster.

## Contributor License Agreement

By submitting this work for inclusion in xfinity-usage, I agree to the following terms:

* The contribution included in this request (and any subsequent revisions or versions of it)
  is being made under the same license as the xfinity-usage project (the Affero GPL v3,
  or any subsequent version of that license if adopted by xfinity-usage).
* My contribution may perpetually be included in and distributed with xfinity-usage; submitting
  this pull request grants a perpetual, global, unlimited license for it to be used and distributed
  under the terms of xfinity-usage's license.
* I have the legal power and rights to agree to these terms.
