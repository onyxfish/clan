==============
clan |release|
==============

About
=====

.. include:: ../README

Installation
============

Users
-----

If you only want to use clan, install it this way::

    pip install clan 

Developers
----------

If you are a developer that also wants to hack on clan, install it this way::

    git clone git://github.com/onyxfish/clan.git
    cd clan
    mkvirtualenv --no-site-packages clan
    pip install -r requirements.txt
    python setup.py develop
    nosetests

.. note::

    If you have a recent version of pip, you may need to run pip with the additional arguments :code:`--allow-external argparse`.
    
Usage
=====

clan has two basic modes, 1) writing analytics data to a JSON file suitable for further processing and 2) writing data to a text report suitable for review or sending in an email. 

To configure clan, create a YAML data file describing the analytics you want to run:

.. code-block:: yaml

    # Global configuration, only property-id is required
    property-id: "53470309"
    start-date: "2014-06-01"
    end-date: "2014-06-04"
    domain: "apps.npr.org"
    prefix: "/commencement/"

    # Metrics to report
    analytics:
        - name: Totals
          metrics:
              - "ga:pageviews"
              - "ga:uniquePageviews"
              - "ga:users"
              - "ga:sessions"
        - name: Totals by device category
          metrics:
              - "ga:pageviews"
              - "ga:uniquePageviews"
              - "ga:users"
              - "ga:sessions"
          dimensions:
              - "ga:deviceCategory"
          sort:
              - "-ga:pageviews"

To run this report to a JSON file:

.. code-block:: bash

    clan -f json analytics.json

To instead produce a text report, run:

.. code-block:: bash

    clan -f txt analytics.txt
    
You can also convert an existing JSON report to text, like so:

.. code-block:: bash

    clan -f txt -d analytics.json analytics.txt

Authors
=======

.. include:: ../AUTHORS

License
=======

.. include:: ../COPYING

Changelog
=========

.. include:: ../CHANGELOG

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

