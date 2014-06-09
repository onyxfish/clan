#!/usr/bin/env python

import argparse
from collections import OrderedDict
import httplib2
import json
import os
import sys 
from time import sleep

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
            '-d', '--data',
            dest='data_path', action='store', default=None,
            help='Path to a existing data file.'
        )

        self.argparser.add_argument(
            '-f', '--format',
            dest='format', action='store', default='txt', choices=['txt', 'json'],
            help='Output format.'
        )

        self.argparser.add_argument(
            '-v', '--verbose',
            dest='verbose', action='store_true',
            help='Print detailed tracebacks when errors occur.'
        )

        self.argparser.add_argument(
            'output',
            action='store',
            help='Output file path.'
        )

        self.args = self.argparser.parse_args(args)

        self._install_exception_handler()

        self.service = self._authorize()

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
        Execute a query.
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

    def report(self):
        """
        Query analytics and stash data in a format suitable for serializing.
        """
        output = {
            'property-id': self.config['property-id'],
            'analytics': [] 
        }

        for analytic in self.config.get('analytics', []):
            print 'Querying "%s"' % analytic['name']

            results = self.query(
                metrics=analytic['metrics'],
                dimensions=analytic.get('dimensions', []),
                filters=analytic.get('filters', None),
                sort=analytic.get('sort', []),
                start_index=analytic.get('start-index', 1),
                max_results=analytic.get('max-results', 10)
            )
            
            dimensions_len = len(analytic.get('dimensions', []))

            data = {
                'config': analytic,
                'sampled': results.get('containsSampledData', False),
                'sampleSize': results.get('sampleSize', None),
                'sampleSpace': results.get('sampleSpace', None),
                'data_types': OrderedDict(),
                'data': OrderedDict()
            }
                    
            for column in results['columnHeaders'][dimensions_len:]:
                data['data_types'][column['name']] = column['dataType']

            def cast_data_type(d, dt):
                if dt == 'INTEGER':
                    return int(d)
                elif data_type == 'TIME' or data_type == 'FLOAT':  
                    return float(d)
                else:
                    raise Exception('Unknown metric data type: %s' % data_type)

            for i, metric in enumerate(analytic['metrics']):
                data['data'][metric] = OrderedDict()
                data_type = data['data_types'][metric]

                if dimensions_len:
                    for row in results.get('rows', []):
                        column = i + dimensions_len
                        label = ','.join(row[:dimensions_len]) 
                        value = cast_data_type(row[column], data_type)

                        data['data'][metric][label] = value 

                data['data'][metric]['total'] = cast_data_type(results['totalsForAllResults'][metric], data_type)

                sleep(1)

            output['analytics'].append(data)

        return output

    def _duration(self, secs):
        """
        Format a duration in seconds as minutes and seconds.
        """
        secs = int(secs)

        if secs > 60:
            mins = secs / 60
            secs = secs - (mins * 60)

            return '%im %02is' % (mins, secs)

        return '%is' % secs

    def _comma(self, d):
        """
        Format a comma separated number.
        """
        return '{:,d}'.format(d)

    def _percent(self, d, t):
        """
        Format a value as a percent of a total.
        """
        return '{:.1%}'.format(float(d) / t)

    def _header(self, s):
        """
        Format a report header.
        """
        return '\n%s\n' % s

    def _three_columns(self, a, b, c):
        """
        Format a three-column layout.
        """
        return '{:>15s}    {:>6s}    {:s}\n'.format(a, b, c)

    def _top_one_metric(self, f, data, total):
        """
        Write summary data one metric.
        """
        for d, v in data.items():
            if total:
                pct = self._percent(v, total)
            else:
                pct = '-'

            f.write(self._three_columns(self._comma(v), pct, d))

    def txt(self, report, f):
        """
        Write report data to a human-readable text file.
        """
        for analytic in report['analytics']:
            f.write(self._header(analytic['config']['name']))

            for metric, data in analytic['data'].items():
                f.write('\n    %s\n' % metric)

                data_type = analytic['data_types'][metric]
                total = data['total']

                for label, value in data.items():
                    if data_type == 'INTEGER':
                        pct = self._percent(value, total) if total > 0 else '0.0%' 
                        value = self._comma(value)
                    elif data_type == 'TIME' or data_type == 'FLOAT':
                        pct = '-'
                        value = self._duration(value)

                    f.write(self._three_columns(value, pct, label))

    def main(self):
        if self.args.data_path:
            with open(self.args.data_path) as f:
                data = json.load(f, object_pairs_hook=OrderedDict)
        else:
            with open(self.args.config_path) as f:
                self.config = yaml.load(f)

            if 'property-id' not in self.config:
                raise Exception('Property ID is required.')

            data = self.report()

        with open(self.args.output, 'w') as f:
            if self.args.format == 'txt':
                self.txt(data, f)
            elif self.args.format == 'json':
                json.dump(data, f, indent=4)

def _main():
    clan = Clan()
    clan.main()
    
if __name__ == "__main__":
    _main()

