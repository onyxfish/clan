===========
Basic usage
===========

clan has three basic uses

* Writing query results to a text report suitable for reading or emailing.
* Writing query results to a JSON file suitable for further processing.
* Generating a "diff", or change report, comparing two sets of query results, as either text or JSON.

Generating a text report
------------------------

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

To instead produce a text report, run:

.. code-block:: bash

    clan report analytics.txt

Here is sample output for the above configuration::

    Report run 2014-06-06 with:
        property-id: 53470309
        start-date: 2014-06-01
        ndays: 2
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

Generating a JSON report
------------------------

Instead of text you can output data in a JSON microformat suitable for archiving, visualization or further processing with other tools:

.. code-block:: bash

    clan report -f json analytics.json

Global configuration options, such as :code:`start-date` can also be specified as command line arguments, allowing you to reuse a YAML configuration file for several projects. When specified, command-line arguments will always take precedence over options defined in the YAML configuration.

.. code-block:: bash

    clan report -f json --start-date 2014-05-1 --prefix /tshirt/ analytics.json 
    
You can also convert an existing JSON report to text, like so:

.. code-block:: bash

    clan report -d analytics.json analytics.txt

Generating a text diff
----------------------

If you report on multiple projects using the same analytics, you can use clan to compare their performance:

.. code-block:: bash

    clan diff a.json b.json diff.txt

This will write a report documenting the absolute and percentage point differences. Here is an example of the output::

    Comparing report A run 2014-06-10 with:
        property-id: 53470309
        start-date: 2014-06-01
        ndays: 2
        prefix: /commencement/

    With report B run 2014-06-10 with:
        property-id: 53470309
        start-date: 2014-06-01
        ndays: 2
        prefix: /tshirt/

    Totals

        ga:sessions
            -12,280    -91.8%         -    total

        ga:pageviews
            -39,514    -96.3%         -    total

        ga:users
            -10,441    -91.9%         -    total

        ga:uniquePageviews
            -27,327    -96.2%         -    total


    Totals by device category

        ga:sessions
             -3,832    -96.6%     -17.3    mobile
            -12,280    -91.8%         -    total
             -1,470    -92.9%      -1.5    tablet
             -6,978    -89.2%      18.8    desktop

        ga:pageviews
             -7,548    -97.8%      -7.5    mobile
            -39,514    -96.3%         -    total
             -4,608    -97.2%      -2.8    tablet
            -27,358    -95.8%      10.3    desktop

        ga:users
             -3,321    -97.1%     -19.4    mobile
            -10,441    -91.9%         -    total
             -1,204    -92.9%      -1.4    tablet
             -5,916    -89.0%      20.8    desktop

        ga:uniquePageviews
             -6,025    -97.8%      -9.1    mobile
            -27,327    -96.2%         -    total
             -3,589    -97.0%      -2.7    tablet
            -17,713    -95.5%      11.8    desktop

The values in the report columns are:

* Absolute difference
* Percent change
* Change in percentage points

Generating a JSON diff
----------------------

As with individual reports, diffs can be saved as JSON for further processing:

.. code-block:: bash

    clan diff -f json a.json b.json diff.json

