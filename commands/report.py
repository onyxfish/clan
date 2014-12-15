#!/usr/bin/env python

from collections import OrderedDict
from datetime import date, datetime, timedelta
import json
import os
from time import sleep
import yaml

from apiclient import discovery
import httplib2
from jinja2 import Environment, PackageLoader
from oauth2client.file import Storage

from commands.utils import GLOBAL_ARGUMENTS, format_comma, format_duration, format_percent

class ReportCommand(object):
    def __init__(self):
        self.args = None
        self.config = None
        self.service = None

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

        input_format = os.path.splitext(self.args.input_path)[1]

        if input_format == '.json':
            with open(self.args.input_path) as f:
                report = json.load(f, object_pairs_hook=OrderedDict)
        elif input_format == '.yml' or input_format == '.yaml':
            with open(self.args.input_path) as f:
                self.config = yaml.load(f)

            if 'property-id' not in self.config:
                raise Exception('You must specify a property-id either in your YAML file or using the --property-id argument.')

            report = self.report()
        else:
            raise Exception('Unsupported input format: %s. Must be .yml or .json.' % input_format)

        output_format = os.path.splitext(self.args.output_path)[1]

        if output_format == '.html':
            with open(self.args.output_path, 'w') as f:
                self.html(report, f)
        elif output_format == '.json':
            with open(self.args.output_path, 'w') as f:
                json.dump(report, f, indent=4)
        else:
            raise Exception('Unsupported output format: %s. Must be .html or .json.' % output_format) 

    def add_argparser(self, root, parents):
        """
        Add arguments for this command.
        """
        parser = root.add_parser('report', parents=parents)
        parser.set_defaults(func=self)

        parser.add_argument(
            '--auth',
            dest='auth', action='store',
            help='Path to the authorized credentials file (analytics.dat).'
        )

        parser.add_argument(
            '-f', '--format',
            dest='format', action='store', default='html', choices=['html', 'json'],
            help='Output format. (Defaults to HTML.)'
        )

        parser.add_argument(
            '--title',
            dest='title', action='store',
            help='User-friendly title for your report.'
        )

        parser.add_argument(
            '--property-id',
            dest='property-id', action='store',
            help='Google Analytics ID of the property to query.'
        )

        parser.add_argument(
            '--start-date',
            dest='start-date', action='store',
            help='Start date for the query in YYYY-MM-DD format.'
        )

        parser.add_argument(
            '--end-date',
            dest='end-date', action='store',
            help='End date for the query in YYYY-MM-DD format. Supersedes --ndays.'
        )

        parser.add_argument(
            '--ndays',
            dest='ndays', action='store', type=int,
            help='The number of days from the start-date to query. Requires start-date. Superseded by end-date.'
        )

        parser.add_argument(
            '--domain',
            dest='domain', action='store',
            help='Restrict results to only urls with this domain.'
        )

        parser.add_argument(
            '--prefix',
            dest='prefix', action='store',
            help='Restrict results to only urls with this prefix.'
        )

        parser.add_argument(
            'input_path',
            action='store',
            help='Path to either a YAML configuration file or pre-reported JSON data.'
        )

        parser.add_argument(
            'output_path',
            action='store',
            help='Path to output either an HTML report or a JSON data file.'
        )

        return parser

    def _ndays(self, start_date, ndays):
        """
        Compute an end date given a start date and a number of days.
        """
        if not getattr(self.args, 'start-date') and not self.config.get('start-date', None):
            raise Exception('start-date must be provided when ndays is used.')

        d = date(*map(int, start_date.split('-')))
        d += timedelta(days=ndays)

        return d.strftime('%Y-%m-%d')

    def query(self, start_date=None, end_date=None, ndays=None, metrics=[], dimensions=[], filters=None, segment=None, sort=[], start_index=1, max_results=10):
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
            segment=segment,
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

        output['title'] = getattr(self.args, 'title') or self.config.get('title', None)
        output['run_date'] = datetime.now().strftime('%Y-%m-%d')
        output['queries'] = []

        for analytic in self.config.get('queries', []):
            print 'Querying "%s"' % analytic['name']

            results = self.query(
                metrics=analytic['metrics'],
                dimensions=analytic.get('dimensions', []),
                filters=analytic.get('filter', None),
                segment=analytic.get('segment', None),
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

    def html(self, report, f):
        """
        Write report data to an HTML file.
        """
        env = Environment(loader=PackageLoader('clan', 'templates'))

        template = env.get_template('report.html')

        context = {
            'report': report,
            'GLOBAL_ARGUMENTS': GLOBAL_ARGUMENTS,
            'format_comma': format_comma,
            'format_duration': format_duration,
            'format_percent': format_percent
        }

        f.write(template.render(**context).encode('utf-8'))


