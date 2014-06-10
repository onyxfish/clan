#!/usr/bin/env python

import argparse
from collections import OrderedDict
from datetime import date, datetime, timedelta
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

GLOBAL_ARGUMENTS = [
    'property-id',
    'start-date',
    'end-date',
    'ndays',
    'domain',
    'prefix',
] 

class Clan(object):
    """
    Command-line interface to Google Analytics.
    """
    def __init__(self):
        """
        Setup and parse command line arguments.
        """
        self._install_exception_handler()

        self.argparser = argparse.ArgumentParser(
            description='A command-line interface to Google Analytics'
        )

        # Generic arguments
        generic_parser = argparse.ArgumentParser(add_help=False)

        generic_parser.add_argument(
            '-v', '--verbose',
            dest='verbose', action='store_true',
            help='Print detailed tracebacks when errors occur.'
        )

        subparsers = self.argparser.add_subparsers()

        # Authentication
        parser_auth = subparsers.add_parser('auth', parents=[generic_parser, tools.argparser])
        parser_auth.set_defaults(func=self.command_auth)

        parser_auth.add_argument(
            '--secrets',
            dest='secrets', action='store',
            help='Path to the authorization secrets file (client_secrets.json).'
        )

        # Reporting
        parser_report = subparsers.add_parser('report', parents=[generic_parser])
        parser_report.set_defaults(func=self.command_report)

        parser_report.add_argument(
            '--auth',
            dest='auth', action='store',
            help='Path to the authorized credentials file (analytics.dat).'
        )

        parser_report.add_argument(
            '-c', '--config',
            dest='config_path', action='store', default='clan.yml',
            help='Path to a YAML configuration file (clan.yml).'
        )

        parser_report.add_argument(
            '-d', '--data',
            dest='data_path', action='store', default=None,
            help='Path to a existing JSON report file.'
        )

        parser_report.add_argument(
            '-f', '--format',
            dest='format', action='store', default='txt', choices=['txt', 'json'],
            help='Output format.'
        )

        parser_report.add_argument(
            '--property-id',
            dest='property-id', action='store',
            help='Google Analytics ID of the property to query.'
        )

        parser_report.add_argument(
            '--start-date',
            dest='start-date', action='store',
            help='Start date for the query in YYYY-MM-DD format.'
        )

        parser_report.add_argument(
            '--end-date',
            dest='end-date', action='store',
            help='End date for the query in YYYY-MM-DD format. Supersedes --ndays.'
        )

        parser_report.add_argument(
            '--ndays',
            dest='ndays', action='store', type=int,
            help='The number of days from the start-date to query. Requires start-date. Superseded by end-date.'
        )

        parser_report.add_argument(
            '--domain',
            dest='domain', action='store',
            help='Restrict results to only urls with this domain.'
        )

        parser_report.add_argument(
            '--prefix',
            dest='prefix', action='store',
            help='Restrict results to only urls with this prefix.'
        )

        parser_report.add_argument(
            'output',
            action='store',
            help='Output file path.'
        )
        
        # Diff
        parser_report = subparsers.add_parser('diff', parents=[generic_parser])
        parser_report.set_defaults(func=self.command_diff)

        parser_report.add_argument(
            '-d', '--data',
            dest='data_path', action='store', default=None,
            help='Path to a existing JSON diff file.'
        )

        parser_report.add_argument(
            '-f', '--format',
            dest='format', action='store', default='txt', choices=['txt', 'json'],
            help='Output format.'
        )

        parser_report.add_argument(
           'report_a',
            action='store',
            help='First JSON report file path.'
        )

        parser_report.add_argument(
           'report_b',
            action='store',
            help='Second JSON report file path.'
        )

        parser_report.add_argument(
            'output',
            action='store',
            help='Output file path.'
        )

        self.args = self.argparser.parse_args()
        self.args.func()

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

    def _ndays(self, start_date, ndays):
        """
        Compute an end date given a start date and a number of days.
        """
        if not getattr(self.args, 'start-date') and not self.config.get('start-date', None):
            raise Exception('start-date must be provided when ndays is used.')

        d = date(*map(int, start_date.split('-')))
        d += timedelta(days=ndays)

        return d.strftime('%Y-%m-%d')

    def query(self, start_date=None, end_date=None, ndays=None, metrics=[], dimensions=[], filters=None, sort=[], start_index=1, max_results=10):
        """
        Execute a query.
        """
        if start_date:
            start_date = start_date
        elif getattr(self.args, 'start-date'):
            start_date = getattr(self.args, 'start-date')
        elif self.config.get('start-date', None):
            start_date = self.config['start-date']
        else:
            start_date = '2005-01-01'

        if end_date:
            end_date = end_date
        elif getattr(self.args, 'end-date'):
            end_date = getattr(self.args, 'end-date')
        elif self.config.get('end-date', None):
            end_date = self.config['end-date']
        elif ndays:
            end_date = self._ndays(start_date, ndays)
        elif self.args.ndays:
            end_date = self._ndays(start_date, self.args.ndays)
        elif self.config.get('ndays', None):
            end_date = self._ndays(start_date, self.config['ndays'])
        else:
            end_date = 'today' 

        if self.args.domain:
            domain = self.args.domain
        elif self.config.get('domain', None):
            domain = self.config['domain']
        else:
            domain = None

        if domain:
            domain_filter = 'ga:hostname==%s' % domain

            if filters:
                filters = '%s;%s' % (domain_filter, filters)
            else:
                filters = domain_filter

        if self.args.prefix:
            prefix = self.args.prefix
        elif self.config.get('prefix', None):
            prefix = self.config['prefix']
        else:
            prefix = None

        if prefix:
            prefix_filter = 'ga:pagePath=~^%s' % prefix 
                
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
        output = OrderedDict()

        for arg in GLOBAL_ARGUMENTS:
            output[arg] = getattr(self.args, arg) or self.config.get(arg, None)

        output['queries'] = []

        for analytic in self.config.get('queries', []):
            print 'Querying "%s"' % analytic['name']

            results = self.query(
                metrics=analytic['metrics'],
                dimensions=analytic.get('dimensions', []),
                filters=analytic.get('filter', None),
                sort=analytic.get('sort', []),
                start_index=analytic.get('start-index', 1),
                max_results=analytic.get('max-results', 10)
            )
            
            dimensions_len = len(analytic.get('dimensions', []))

            data = OrderedDict([ 
                ('config', analytic),
                ('sampled', results.get('containsSampledData', False)),
                ('sampleSize', int(results.get('sampleSize', 0))),
                ('sampleSpace', int(results.get('sampleSpace', 0))),
                ('data_types', OrderedDict()),
                ('data', OrderedDict())
            ])
                    
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

            output['queries'].append(data)

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
    
        for var in GLOBAL_ARGUMENTS:
            if report.get(var, None):
                f.write('    %s: %s\n' % (var , report[var]))

        f.write('\n')

        for analytic in report['queries']:
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

    def diff(self, report_a, report_b):
        """
        Generate a diff for two data reports.
        """

        output = OrderedDict([
            ('a', OrderedDict([(arg, report_a[arg]) for arg in GLOBAL_ARGUMENTS])),
            ('b', OrderedDict([(arg, report_b[arg]) for arg in GLOBAL_ARGUMENTS])),
            ('queries', [])
        ])

        for query_a in report_a['queries']:
            for query_b in report_b['queries']:
                if query_a['config'] == query_b['config']:
                    print 'match'

            query_b = report_b['queries']

        return output 

    def txt_diff(self, diff):
        """
        Generate a text report for a diff.
        """
        pass

    def command_auth(self):
        """
        Authorize with Google Analytics.
        """
        if not self.args.secrets:
            home_path = os.path.expanduser('~/.clan_secrets.json')

            if os.path.exists('client_secrets.json'):
                self.args.secrets = 'client_secrets.json'
            elif os.path.exists(home_path):
                self.args.secrets = home_path
            else:
                raise Exception('Could not locate authentication secrets (client_secrets.jsonn). Please create it or specify a different file using --secrets.')

        storage = Storage('analytics.dat')
        
        flow = client.flow_from_clientsecrets(
            self.args.secrets,
            scope='https://www.googleapis.com/auth/analytics.readonly'
        )
        
        tools.run_flow(flow, storage, self.args)

    def command_report(self):
        """
        Report out data.
        """
        if not self.args.auth:
            home_path = os.path.expanduser('~/.clan_auth.dat')

            if os.path.exists('analytics.dat'):
                self.args.auth = 'analytics.dat'
            elif os.path.exists(home_path):
                self.args.auth = home_path
            else:
                raise Exception('Could not locate local authorization token (analytics.dat). Please specify it using --auth or run "clan auth".')

        storage = Storage(self.args.auth)
        credentials = storage.get()

        if not credentials or credentials.invalid:
            raise Exception('Invalid authentication. Please run "clan auth" to generate a new token.')

        http = credentials.authorize(http=httplib2.Http())
        self.service = discovery.build('analytics', 'v3', http=http)

        if self.args.data_path:
            with open(self.args.data_path) as f:
                report = json.load(f, object_pairs_hook=OrderedDict)
        else:
            with open(self.args.config_path) as f:
                self.config = yaml.load(f)

            if 'property-id' not in self.config:
                raise Exception('You must specify a property-id either in your YAML file or using the --property-id argument.')

            report = self.report()

        with open(self.args.output, 'w') as f:
            if self.args.format == 'txt':
                self.txt(report, f)
            elif self.args.format == 'json':
                json.dump(report, f, indent=4)

    def command_diff(self):
        """
        Compare two data files and generate a report of their differences.
        """
        if self.args.data_path:
            with open(self.args.data_path) as f:
                diff = json.load(f, object_pairs_hook=OrderedDict)
        else:
            with open(self.args.report_a) as f:
                report_a = json.load(f)

            with open(self.args.report_b) as f:
                report_b = json.load(f)

            diff = self.diff(report_a, report_b)

        with open(self.args.output, 'w') as f:
            if self.args.format == 'txt':
                self.txt_diff(diff, f)
            elif self.args.format == 'json':
                json.dump(diff, f, indent=4)

def _main():
    Clan()
    
if __name__ == "__main__":
    _main()

