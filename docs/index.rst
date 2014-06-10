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

Once you've got a :code:`client_secrets.json` file, clan will walk you through acquiring an oAuth token:

.. code-block:: bash

    clan auth

By default this token will be named :code:`analytics.dat`. I suggest you move this file to :code:`~/.clan_auth.dat`. clan will always look for the auth in that location so you will only need one copy no matter what directory you are running clan from.
    
Basic usage
===========

clan has two basic modes, 1) writing analytics data to a JSON file suitable for further processing and 2) writing data to a text report suitable for reading or emailing. 

To configure clan, create a YAML data file describing the analytics you want to run:

.. code-block:: yaml

    # Global configuration, only property-id is required
    property-id: "53470309"
    start-date: "2014-06-01"
    prefix: "/commencement/"

    # Metrics to report
    queries:
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

To run this report to a JSON file, run the following command. Note that by default clan will look for a YAML file called :code:`clan.yml`. You can override this with the :code:`-c` option. For complete documenation of this configuration, see :doc:`Configuration <configuration>`.

.. code-block:: bash

    clan report -f json analytics.json

Global configuration can also be specified as command arguments, allowing you to reuse a YAML configuration file for several properties or page sets. When specified, command-line arguments will always take precedence over variables in the YAML configuration.

.. code-block:: bash

    clan report -f json --start-date 2014-05-1 --prefix /tshirt/ analytics.json 

To instead produce a text report (the default), run:

.. code-block:: bash

    clan report analytics.txt
    
You can also convert an existing JSON report to text, like so:

.. code-block:: bash

    clan report -d analytics.json analytics.txt

Here is sample output for the above configuration::

    Report run 2014-06-06 with:
        property-id: 53470309
        start-date: 2014-06-01
        prefix: /commencement/

    Totals
    (using 89.0% of data as sample)

        ga:pageviews
             88,935    100.0%    total

        ga:uniquePageviews
             60,179    100.0%    total

        ga:users
             21,244    100.0%    total

        ga:sessions
             26,817    100.0%    total


    Totals by device category
    (using 89.0% of data as sample)

        ga:pageviews
             64,542     72.6%    desktop
             15,403     17.3%    mobile
              8,991     10.1%    tablet
             88,936    100.0%    total

        ga:uniquePageviews
             40,966     68.1%    desktop
             12,277     20.4%    mobile
              6,936     11.5%    tablet
             60,179    100.0%    total

        ga:users
             12,838     60.4%    desktop
              6,084     28.6%    mobile
              2,322     10.9%    tablet
             21,244    100.0%    total

        ga:sessions
             16,014     59.7%    desktop
              7,644     28.5%    mobile
              3,159     11.8%    tablet
             26,817    100.0%    total

Advanced usage
==============

.. toctree::

    configuration

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

