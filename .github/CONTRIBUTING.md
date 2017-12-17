Contributing to xfinity-usage
===============================

Contributions are gladly accepted. At the moment this is really just a package around
a simple script, and unforunately the only testing currently in place is pep8/pyflakes
and a relatively simple import test.

Release Process
---------------

The release process is manual for the time being. It's being documented here in
case this project ever gets a co-maintainer.

1. Ensure tests pass (when we have them; for now, ensure the script works).
2. Ensure a ``CHANGELOG.rst`` entry exists for all changes.
3. Bump the version in ``xfinity_usage/version.py``.
4. Commit that and push to master.
5. Upload package to testpypi:

   * Make sure your ~/.pypirc file is correct (a repo called ``test`` for https://testpypi.python.org/pypi)
   * ``rm -Rf dist``
   * ``python setup.py sdist bdist_wheel``
   * ``twine upload -r test dist/*``
   * Check that the README renders at https://testpypi.python.org/pypi/xfinity-usage

6. Tag the release in Git (using a signed tag), push tag to GitHub:

   * tag the release with a signed tag: ``git tag -s -a X.Y.Z -m 'X.Y.Z released YYYY-MM-DD'``
   * verify the signature: ``git tag -v X.Y.Z``
   * push the tag to GitHub: ``git push origin X.Y.Z``

7. Upload package to live pypi:

    * ``twine upload dist/*``
