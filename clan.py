#!/usr/bin/env python

import argparse
import datetime
import httplib2
import os
import sys 

from apiclient import discovery
from oauth2client import client
from oauth2client.clientsecrets import InvalidClientSecretsError
from oauth2client.file import Storage
from oauth2client import tools

CLIENT_SECRETS = os.path.expanduser('~/.google_analytics_secrets.json')
DAT = os.path.expanduser('~/.google_analytics_auth.dat')

SERVICE_NAME = 'analytics'
SERVICE_VERSION = 'v3'
SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
NPR_ORG_LIVE_ID = '53470309'

class Clan(object):

    def __init__(self, args=None, output_file=None):
        """
        Setup.
        """
        self.argparser = argparse.ArgumentParser(
            description='TKTK',
            epilog='TKTK',
            parents=[tools.argparser]
        )

        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
            help='Display column names and indices from the input CSV and exit.')

        self.args = self.argparser.parse_args(args)

        self._install_exception_handler()

        self.service = self._authorize()

        self.property_id = NPR_ORG_LIVE_ID 
        self.domain = None 
        self.slug = None
        self.start_date = None
        self.end_date = None

    def _install_exception_handler(self):
        """
        Installs a replacement for sys.excepthook, which handles pretty-printing uncaught exceptions.
        """
        def handler(t, value, traceback):
            if self.args.verbose:
                sys.__excepthook__(t, value, traceback)
            else:
                sys.stderr.write('%s\n' % unicode(value).encode('utf-8'))

        sys.excepthook = handler

    def _authorize(self):
        """
        Authorize with OAuth2.
        """
        storage = Storage(DAT)
        credentials = storage.get()
        
        if not credentials or credentials.invalid:
            try:
                flow = client.flow_from_clientsecrets(
                    CLIENT_SECRETS,
                    scope=SCOPE
                )
            except InvalidClientSecretsError:
                print 'Client secrets not found at %s' % CLIENT_SECRETS
            
            credentials = tools.run_flow(flow, storage, self.args)
            
        http = credentials.authorize(http=httplib2.Http())
    
        return discovery.build(SERVICE_NAME, SERVICE_VERSION, http=http)

    def query(self, start_date=None, end_date=None, metrics=[], dimensions=[], filters=None, sort=[], start_index=1, max_results=10):
        """
        Execute a query
        """
        if start_date:
            start_date = start_date.strftime('%Y-%m-%d')
        elif self.start_date:
            start_date = self.start_date.strftime('%Y-%m-%d')
        else:
            start_date = '2005-01-01'

        if end_date:
            end_date = end_date.strftime('%Y-%m-%d')
        elif self.end_date:
            end_date = self.end_date.strftime('%Y-%m-%d')
        else:
            end_date = 'today' 

        if self.domain:
            domain_filter = 'ga:hostname=%s' % self.domain

            if filters:
                filters = '%s;%s' % (domain_filter, filters)
            else:
                filters = domain_filter

        if self.slug:
            slug_filter = 'ga:pagePath=~^/%s/' % self.slug
                
            if filters:
                filters = '%s;%s' % (slug_filter, filters)
            else:
                filters = slug_filter

        return self.service.data().ga().get(
            ids='ga:' + self.property_id,
            start_date=start_date,
            end_date=end_date,
            metrics=','.join(metrics) or None,
            dimensions=','.join(dimensions) or None,
            filters=filters,
            sort=','.join(sort) or None,
            start_index=str(start_index),
            max_results=str(max_results)
        ).execute()


    def main(self):
        print self.query(
            start_date=datetime.date(2014, 6, 1),
            metrics=['ga:pageviews']
        ) 
                
def _main():
    clan = Clan()
    clan.main()
    
if __name__ == "__main__":
    _main()

