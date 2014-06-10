==============
Authentication
==============

Before you use clan, you're going to need to setup your access to the Google Analytics API. Follow the `instructions in Google's docs <https://developers.google.com/analytics/solutions/articles/hello-analytics-api#register_project>`_ to register an application and create the :code:`client_secrets.json` file.

Once you've got a :code:`client_secrets.json` file, clan will walk you through acquiring an oAuth token:

.. code-block:: bash

    clan auth

By default this token will be named :code:`analytics.dat`. I suggest you move this file to :code:`~/.clan_auth.dat`. clan will always look for the auth in that location so you will only need one copy no matter what directory you are running clan from.
    

