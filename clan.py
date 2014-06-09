#!/usr/bin/env python

import argparse
from collections import OrderedDict
import httplib2
import json
import os
import sys 

from apiclient import discovery
from oauth2client import client
from oauth2client.clientsecrets import InvalidClientSecretsError
from oauth2client.file import Storage
from oauth2client import tools
import yaml

CLIENT_SECRETS = os.path.expanduser('~/.google_analytics_secrets.json')
DAT = os.path.expanduser('~/.google_analytics_auth.dat')

SERVICE_NAME = 'analytics'
SERVICE_VERSION = 'v3'
SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
NPR_ORG_LIVE_ID = '53470309'

class Clan(object):
    """
    Command-line interface to Google Analytics.
    """
    def __init__(self, args=None, output_file=None):
        """
        Setup.
        """
        self.argparser = argparse.ArgumentParser(
            description='TKTK',
            epilog='TKTK',
            parents=[tools.argparser]
        )

        self.argparser.add_argument(
            '-c', '--config',
            dest='config_path', action='store', default='clan.yaml',
            help='Path to a YAML configuration file.'
        )

        self.argparser.add_argument(
            '-v', '--verbose',
            dest='verbose', action='store_true',
            help='Print detailed tracebacks when errors occur.'
        )

        self.args = self.argparser.parse_args(args)

        self._install_exception_handler()

        self.service = self._authorize()

        with open(self.args.config_path) as f:
            self.config = yaml.load(f)

        if 'property-id' not in self.config:
            raise 'Property ID is required.'

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
            start_date = start_date
        elif self.config.get('start-date', None):
            start_date = self.config['start-date']
        else:
            start_date = '2005-01-01'

        if end_date:
            end_date = end_date
        elif self.config.get('end-date', None):
            end_date = self.config['end-date']
        else:
            end_date = 'today' 

        if self.config.get('domain', None):
            domain_filter = 'ga:hostname=%s' % self.config['domain']

            if filters:
                filters = '%s;%s' % (domain_filter, filters)
            else:
                filters = domain_filter

        if self.config.get('slug', None):
            slug_filter = 'ga:pagePath=~^/%s/' % self.config['slug']
                
            if filters:
                filters = '%s;%s' % (slug_filter, filters)
            else:
                filters = slug_filter

        return self.service.data().ga().get(
            ids='ga:' + self.config['property-id'],
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
        output = {
            'property-id': self.config['property-id'],
            'analytics': [] 
        }

        for analytic in self.config.get('analytics', []):
            print 'Querying "%s"' % analytic['name']

            results = self.query(
                metrics=analytic['metrics'],
                dimensions=analytic.get('dimensions', []),
                sort=analytic.get('sort', [])
            )

            data = {
                'config': analytic,
                'data': OrderedDict()
            }
                    
            dimensions_len = len(analytic.get('dimensions', []))

            for i, metric in enumerate(analytic['metrics']):
                data['data'][metric] = OrderedDict()

                if dimensions_len:
                    for row in results.get('rows', []):
                        column = i + dimensions_len
                        label = ','.join(row[:dimensions_len]) 

                        data['data'][metric][label] = int(row[column])

                data['data'][metric]['all'] = results['totalsForAllResults'][metric]

            output['analytics'].append(data)

        with open('analytics.json', 'w') as f:
            json.dump(output, f, indent=4)

def _main():
    clan = Clan()
    clan.main()
    
if __name__ == "__main__":
    _main()

