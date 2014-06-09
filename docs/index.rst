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

Here is sample output for the above configuration:

.. code-block::

    Report run 2014-06-06 with:
        property-id: 53470309
        start-date: 2014-06-01

    Totals

        ga:pageviews
         26,549,529    100.0%    total

        ga:uniquePageviews
         16,650,481    100.0%    total

        ga:users
          6,778,073    100.0%    total

        ga:sessions
         11,228,183    100.0%    total


    Totals by device category
    (using 89.0% of data as sample)

        ga:pageviews
         19,651,273     74.7%    desktop
          4,850,906     18.4%    mobile
          1,802,445      6.9%    tablet
         26,304,624    100.0%    total

        ga:uniquePageviews
         10,764,238     65.3%    desktop
          4,237,022     25.7%    mobile
          1,484,038      9.0%    tablet
         16,485,298    100.0%    total

        ga:users
          3,741,112     54.8%    desktop
          2,357,376     34.5%    mobile
            726,753     10.6%    tablet
          6,825,241    100.0%    total

        ga:sessions
          6,492,857     58.4%    desktop
          3,548,599     31.9%    mobile
          1,079,451      9.7%    tablet
         11,120,907    100.0%    total


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

