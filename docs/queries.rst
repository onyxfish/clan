==============
Common queries
==============

Total pageviews, uniques, users, etc.
-------------------------------------

.. code-block:: yaml

    - name: Totals
      metrics:
          - "ga:pageviews"
          - "ga:uniquePageviews"
          - "ga:users"
          - "ga:sessions"

Device share
------------

Get totals broken down by :code:`desktop`, :code:`tablet` and :code:`mobile`.

.. code-block:: yaml

    - name: Totals by device type 
      metrics:
          - "ga:pageviews"
          - "ga:uniquePageviews"
          - "ga:users"
          - "ga:sessions"
      dimensions:
          - "ga:deviceCategory"
      sort:
          - "-ga:pageviews"

Browser share
-------------

.. code-block:: yaml

   - name: Totals by browser 
      metrics:
          - "ga:pageviews"
      dimensions:
          - "ga:browser"
      sort:
          - "-ga:pageviews"

Most viewed pages
-----------------

.. code-block:: yaml

    - name: Top pages 
      metrics:
          - "ga:pageviews"
      dimensions:
          - "ga:pagePath"
      sort:
          - "-ga:pageviews"
      max-results: 20

Top sources (referrers)
-----------------------

.. code-block:: yaml

    - name: Totals by source 
      metrics:
          - "ga:pageviews"
      dimensions:
          - "ga:source"
      sort:
          - "-ga:pageviews"

Top social sources
------------------

.. code-block:: yaml

    - name: Totals by social network 
      metrics:
          - "ga:pageviews"
      dimensions:
          - "ga:socialNetwork"
      sort:
          - "-ga:pageviews"

Page load
---------

.. code-block:: yaml

    - name: Performance
      metrics:
          - "ga:avgPageLoadTime"
          - "ga:avgPageDownloadTime"
          - "ga:avgDomInteractiveTime"
          - "ga:avgDomContentLoadedTime"

Time on site
------------

.. code-block:: yaml

    - name: Time on site
      metrics:
          - "ga:avgSessionDuration"

Custom event count
------------------

.. code-block:: yaml

    - name: "Event: tweet"
      metrics:
          - "ga:totalEvents"
          - "ga:uniqueEvents"
      filter: "ga:eventAction==tweet"

Custom event value
------------------

.. code-block:: yaml

    - name: "Event: time-on-slide"
      metrics:
          - "ga:eventValue"
          - "ga:avgEventValue"
      filter: "ga:eventAction==time-on-slide"

