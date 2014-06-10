#!/usr/bin/env python

from collections import OrderedDict
from datetime import date, datetime, timedelta
import json
import os
from time import sleep
import yaml

from apiclient import discovery
import httplib2
from oauth2client.file import Storage

from commands.utils import GLOBAL_ARGUMENTS

class ReportCommand(object):
    def __init__(self):
        self.args = None
        self.config = None
        self.service = None

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

    def __call__(self, args):
        self.args = args

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
