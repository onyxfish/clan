=============
Configuration
=============

Configuring clan
================

clan is configured using either YAML, command-line arguments or both.

By default clan will look for a YAML file called :code:`clan.yml`. This can be configured using the :code:`-c` command line flag. The basic structure of this file is:

.. code-block: yaml

    # Global configuration
    property-id: "53470309"

    # A list of queries to execute
    queries:

        # Individual query configuration
        - name: Totals
          metrics:
              - "ga:pageviews"
              - "ga:uniquePageviews"
              - "ga:users"
              - "ga:sessions"

Global configuration
====================

The following is a list of properties that may be specified in as global configuration. Note that these may also be specified using command line arguments. Some properties can also be specified on a per-query basis. If there is a disagreement, the values will be preferred in the following order:

* Command-line values
* Query configuration in YAML
* Global configuration in YAML

property-id
-----------

The ID of the Google Analytics property to query.

start-date
----------

The start date of all queries, in YYYY-MM-DD format.

end-date
--------

The end date of all queries, in YYYY-MM-DD format.

domain
------

If specified, results will be limited to URLs from this domain.

prefix
------

If specified, results will be limited to URLs with this prefix.

Query configuration
===================

Individual queries support the following properties.

name
----

A description of the query. Will be used as a display name when rendering a text report.

metrics
-------

A list of Google Analytics metrics to be reported. 

For details about all metrics you can report on, see the `Google Analytics Core Reporting API docs <https://developers.google.com/analytics/devguides/reporting/core/dimsmets>`_.

dimensions
----------

A list of Google Analytics metrics on which to segment the data. Not that these are pairwise not hierarchical. If your query configuration looked like:

.. code-block:: yaml

    - name: Pageviews by device and browser
      metrics:
          - "ga:pageviews"
      dimensions:
          - "ga:deviceCategory"
          - "ga:browser"
      sort:
          - "-ga:pageviews"

Then your resulting report would enumerate the most popular combinations of device and browser, not the most popular devices further subdivided by most popular browser. 

sort
----

A list of Google Analytics metrics to sort by. Prefix a value with a :code:`-` to sort in descending order. 

filter
------

A Google Analytics `query filter expression <https://developers.google.com/analytics/devguides/reporting/core/v3/reference#filters>`_ to apply to the data. This will be "ANDed" togther with any filters automatically generated from other configuration options such as :code:`domain` or :code:`prefix`.

