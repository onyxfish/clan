===========
Basic usage
===========

clan has three basic uses

* Writing query results to an text or HTML report suitable for reading.
* Writing query results to a JSON file suitable for further processing.
* Generating an HTML "diff", or change report, comparing two JSON outputs. 

Generating a text report
------------------------

To configure clan, create a YAML data file describing the analytics you want to run:

.. code-block:: yaml

    # Global configuration, only property-id is required
    title: Commencement report
    property-id: "53470309"
    start-date: "2014-06-01"
    prefix: "/commencement/"

    # Metrics to report
    queries:
        - name: Totals
          description: Top-level counts
          metrics:
              - "ga:pageviews"
              - "ga:uniquePageviews"
              - "ga:users"
              - "ga:sessions"

        - name: Totals by device category
          description: Device categories are desktop, tablet and mobile
          metrics:
              - "ga:pageviews"
              - "ga:uniquePageviews"
              - "ga:users"
              - "ga:sessions"
          dimensions:
              - "ga:deviceCategory"
          sort:
              - "-ga:pageviews"

Assuming this configuration is named "configuration.yml", to produce an HTML report for this configuration you would run the following command. 

.. code-block:: bash

    clan report configuration.yml report.html

For complete documenation of this configuration, see :doc:`Configuration <configuration>`.

Generating a JSON report
------------------------

Instead of HTML you can output data in a JSON microformat suitable for diffing, archiving, visualization or further processing with other tools:

.. code-block:: bash

    clan report configuration.yml report.json

Global configuration options, such as :code:`start-date` can also be specified as command line arguments, allowing you to reuse a YAML configuration file for several projects. When specified, command-line arguments will always take precedence over options defined in the YAML configuration.

.. code-block:: bash

    clan report --start-date 2014-05-1 --prefix /tshirt/ configuration.yml report.json 
    
You can also convert an HTML report from an existing JSON report:

.. code-block:: bash

    clan report analytics.json report.html

Generating a text diff
----------------------

If you report on multiple projects using the same analytics, you can use clan to compare their performance:

.. code-block:: bash

    clan diff a.json b.json diff.html

The values in the diff report columns will be: 

* Absolute difference
* Percent change
* Change in percentage points

Generating a JSON diff
----------------------

As with individual reports, diffs can also be saved as JSON for further processing:

.. code-block:: bash

    clan diff a.json b.json diff.json

