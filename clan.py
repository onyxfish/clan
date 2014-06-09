#!/usr/bin/env python

import argparse
from collections import OrderedDict
from datetime import datetime
import httplib2
import json
import os
import sys 
from time import sleep

from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage
from oauth2client import tools
import yaml

class Clan(object):
    """
    Command-line interface to Google Analytics.
    """
    def __init__(self, args=None, output_file=None):
        """
        Setup.
        """
        self.argparser = argparse.ArgumentParser(
            description='A command-line interface to Google Analytics',
            parents=[tools.argparser]
        )

        self.argparser.add_argument(
            '--auth',
            dest='auth', action='store',
            help='Path to the authorized credentials file (analytics.dat).'
        )

        self.argparser.add_argument(
            '--secrets',
            dest='secrets', action='store',
            help='Path to the authorization secrets file (client_secrets.json).'
        )

        self.argparser.add_argument(
            '-c', '--config',
            dest='config_path', action='store', default='clan.yaml',
            help='Path to a YAML configuration file.'
        )

        self.argparser.add_argument(
            '-d', '--data',
            dest='data_path', action='store', default=None,
            help='Path to a existing JSON report file.'
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
            nargs='?', action='store',
            help='Output file path.'
        )

        self.args = self.argparser.parse_args(args)

        if not self.args.auth:
            home_path = os.path.expanduser('~/.google_analytics_auth.dat')

            if os.path.exists('analytics.dat'):
                self.args.auth = 'analytics.dat'
            elif os.path.exists(home_path):
                self.args.auth = home_path

        if not self.args.secrets:
            home_path = os.path.expanduser('~/.google_analytics_secrets.json')

            if os.path.exists('client_secrets.json'):
                self.args.secrets = 'client_secrets.json'
            elif os.path.exists(home_path):
                self.args.secrets = home_path

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
        if self.args.auth:
            storage = Storage(self.args.auth)
            credentials = storage.get()
        else:
            if not self.args.secrets:
                raise Exception('Could not locate either analytics.dat or client_secrets.json')
        
        if not self.args.auth or not credentials or credentials.invalid:
            storage = Storage('analytics.dat')
            
            flow = client.flow_from_clientsecrets(
                self.args.secrets,
                scope='https://www.googleapis.com/auth/analytics.readonly'
            )
            
            credentials = tools.run_flow(flow, storage, self.args)
            
        http = credentials.authorize(http=httplib2.Http())
    
        return discovery.build('analytics', 'v3', http=http)

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
            domain_filter = 'ga:hostname==%s' % self.config['domain']

            if filters:
                filters = '%s;%s' % (domain_filter, filters)
            else:
                filters = domain_filter

        if self.config.get('prefix', None):
            prefix_filter = 'ga:pagePath=~^%s' % self.config['prefix']
                
            if filters:
                filters = '%s;%s' % (prefix_filter, filters)
            else:
                filters = prefix_filter

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
            'start-date': self.config.get('start-date', None),
            'end-date': self.config.get('end-date', None),
            'domain': self.config.get('domain', None),
            'prefix': self.config.get('prefix', None),
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
                'sampleSize': int(results.get('sampleSize', 0)),
                'sampleSpace': int(results.get('sampleSpace', 0)),
                'data_types': OrderedDict(),
                'data': OrderedDict()
            }
                    
            for column in results['columnHeaders'][dimensions_len:]:
                data['data_types'][column['name']] = column['dataType']

            def cast_data_type(d, dt):
                if dt == 'INTEGER':
                    return int(d)
                elif data_type in ['TIME', 'FLOAT', 'CURRENCY', 'PERCENT']:  
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

                # Prevent rate-limiting
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

    def txt(self, report, f):
        """
        Write report data to a human-readable text file.
        """
        f.write('Report run %s with:\n' % datetime.now().strftime('%Y-%m-%m'))
    
        for var in ['property-id', 'start-date', 'end-date', 'domain', 'prefix']:
            if report.get(var, None):
                f.write('    %s: %s\n' % (var , report[var]))

        f.write('\n')

        for analytic in report['analytics']:
            f.write('%s\n' % analytic['config']['name'])

            if analytic['sampled']:
                f.write('(using {:.1%} of data as sample)\n'.format(float(analytic['sampleSize']) / analytic['sampleSpace']))
                
            f.write('\n')

            for metric, data in analytic['data'].items():
                f.write('    %s\n' % metric)

                data_type = analytic['data_types'][metric]
                total = data['total']

                for label, value in data.items():
                    if data_type == 'INTEGER':
                        pct = self._percent(value, total) if total > 0 else '0.0%' 
                        value = self._comma(value)
                    elif data_type == 'TIME':
                        pct = '-'
                        value = self._duration(value)
                    elif data_type in ['FLOAT', 'CURRENCY', 'PERCENT']:
                        pct = '-'
                        value = '%.1f' % value

                    f.write('{:>15s}    {:>6s}    {:s}\n'.format(value, pct, label))

                f.write('\n')

            f.write('\n')

    def main(self):
        if not self.args.output:
            return

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

