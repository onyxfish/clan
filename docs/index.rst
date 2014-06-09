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

.. note::

    clan is intended for **researchers** and **analysts**. You will need to understand the Google Analytics API in order to use it effectively. It is not intended to generate reports for your boss.

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

Authentication
==============

Before you use clan, you're going to need to setup your access to the Google Analytics API. Follow the `instructions in Google's docs <https://developers.google.com/analytics/solutions/articles/hello-analytics-api#register_project>`_ to register an application and create the :code:`client_secrets.json` file.

Once you've got a :code:`client_secrets.json` file, simple run clan and it will acquire an oAuth token for you.

.. code-block:: bash

    clan

By default this token will be named :code:`analytics.dat`. I suggest you move this file to :code:`~/.google_analytics_auth.dat`. clan will always look for the auth in that location so you will only need one copy no matter what directory you are running clan from.
    
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
    prefix: "/best-books-2013/"

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

.. note::

    For details about all metrics you can report on, see the `Google Analytics Core Reporting API docs <https://developers.google.com/analytics/devguides/reporting/core/dimsmets>`_.

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

