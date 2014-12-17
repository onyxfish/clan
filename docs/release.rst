===============
Release process
===============

#. Verify no high priority issues are outstanding.
#. Ensure these files all have the correct version number:
    * ``CHANGELOG``
    * ``setup.py``
    * ``docs/conf.py``
    * ``clan/templates/report.html`` (footer)
    * ``clan/templates/diff.html`` (footer)
#. Tag the release: ``git tag -a x.y.z; git push --tags``
#. Roll out to PyPI: ``python setup.py sdist upload``
#. Iterate the version number in all files where it is specified. (see list above)
#. Flag the new version for building on `Read the Docs <https://readthedocs.org/dashboard/clan/versions/>`_. 
#. Wait for the documentation build to finish.
#. Flag the new release as the default documentation version.
#. Announce the release on Twitter, etc. 

