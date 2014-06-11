#!/usr/bin/env python

from collections import OrderedDict
import json

from jinja2 import Environment, PackageLoader

from commands.utils import GLOBAL_ARGUMENTS, format_comma, format_duration, format_percent

class DiffCommand(object):
    def __init__(self):
        self.args = None
    
    def __call__(self, args):
        """
        Compare two data files and generate a report of their differences.
        """
        self.args = args

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
                self.txt(diff, f)
            elif self.args.format == 'html':
                self.html(diff, f)
            elif self.args.format == 'json':
                json.dump(diff, f, indent=4)

    def add_argparser(self, root, parents):
        """
        Add arguments for this command.
        """
        parser = root.add_parser('diff', parents=parents)
        parser.set_defaults(func=self)

        parser.add_argument(
            '--secrets',
            dest='secrets', action='store',
            help='Path to the authorization secrets file (client_secrets.json).'
        )

        parser.add_argument(
            '-d', '--data',
            dest='data_path', action='store', default=None,
            help='Path to a existing JSON diff file.'
        )

        parser.add_argument(
            '-f', '--format',
            dest='format', action='store', default='txt', choices=['txt', 'json', 'html'],
            help='Output format.'
        )

        parser.add_argument(
           'report_a',
            action='store',
            help='First JSON report file path.'
        )

        parser.add_argument(
           'report_b',
            action='store',
            help='Second JSON report file path.'
        )

        parser.add_argument(
            'output',
            action='store',
            help='Output file path.'
        )

        return parser

    def diff(self, report_a, report_b):
        """
        Generate a diff for two data reports.
        """

        arguments = GLOBAL_ARGUMENTS + ['run_date']

        output = OrderedDict([
            ('a', OrderedDict([(arg, report_a[arg]) for arg in arguments])),
            ('b', OrderedDict([(arg, report_b[arg]) for arg in arguments])),
            ('queries', [])
        ])

        output['a']

        for query_a in report_a['queries']:
            for query_b in report_b['queries']:
                if query_a['config'] == query_b['config']:
                    diff = OrderedDict()

                    diff['config'] = query_a['config']
                    diff['data_types'] = query_a['data_types']
                    diff['data'] = OrderedDict()

                    for metric, values in query_a['data'].items():
                        diff['data'][metric] = OrderedDict()

                        for label, value in values.items():
                            diff['data'][metric][label] = OrderedDict([
                                ('a', value),
                                ('b', query_b['data'][metric][label])
                            ])

                    output['queries'].append(diff)

            query_b = report_b['queries']

        return output 

    def txt(self, diff, f):
        """
        Generate a text report for a diff.
        """
        env = Environment(
            loader=PackageLoader('clan', 'templates'),
            trim_blocks=True,
            lstrip_blocks=True
        )

        template = env.get_template('diff.txt')

        def format_row(label, values, totals, data_type):
            a = values['a']
            b = values['b']

            change = b - a 

            if data_type == 'INTEGER':
                pct_a = float(a) / totals['a'] if totals['a'] > 0 else None 
                pct_b = float(b) / totals['b'] if totals['b'] > 0 else None

                pct = '{:.1%}'.format(float(change) / a) if a > 0 else '-'

                if label == 'total' or pct_a is None or pct_b is None:
                    pts = '-'
                else:
                    pts = '{:.1f}'.format((pct_b - pct_a) * 100)

                value = format_comma(change)
            elif data_type == 'TIME':
                pct = '{:.1%}'.format(float(change) / a) if a > 0 else '-' 
                pts = '-'
                value = format_duration(change)
            elif data_type in ['FLOAT', 'CURRENCY', 'PERCENT']:
                pct = '{:.1%}'.format(float(change) / a) if a > 0 else '-' 
                pts = '-'
                value = '%.1f' % change 

            if change > 0:
                value = '+%s' % value 

            return '{:>15s}    {:>6s}    {:>6s}    {:s}\n'.format(value, pct, pts, label)

        context = {
            'diff': diff,
            'GLOBAL_ARGUMENTS': GLOBAL_ARGUMENTS,
            'format_comma': format_comma,
            'format_duration': format_duration,
            'format_percent': format_percent,
            'format_row': format_row
        }

        f.write(template.render(**context))

    def html(self, diff, f):
        """
        Generate a text report for a diff.
        """
        env = Environment(loader=PackageLoader('clan', 'templates'))

        template = env.get_template('diff.html')

        context = {
            'diff': diff,
            'GLOBAL_ARGUMENTS': GLOBAL_ARGUMENTS,
            'format_comma': format_comma,
            'format_duration': format_duration,
            'format_percent': format_percent
        }

        f.write(template.render(**context))

