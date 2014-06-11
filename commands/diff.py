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

                        total_a = values['total']
                        total_b = query_b['data'][metric]['total']

                        for label, value in values.items():
                            a = value
                            b = query_b['data'][metric][label]

                            change = b - a
                            percent_change = float(change) / a if a > 0 else None
                            
                            percent_a = float(a) / total_a if total_a > 0 else None
                            percent_b = float(b) / total_b if total_b > 0 else None

                            if label == 'total' or percent_a is None or percent_b is None:
                                point_change = None
                            else:
                                point_change = percent_b - percent_a

                            diff['data'][metric][label] = OrderedDict([
                                ('change', change),
                                ('percent_change', percent_change),
                                ('point_change', point_change),
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

        def format_row(label, values):
            change = format_comma(values['change'])
            percent_change = '{:.1%}'.format(values['percent_change']) if values['percent_change'] is not None else '-'
            point_change = '{:.1f}'.format(values['point_change']) if values['point_change'] is not None else '-'

            return '{:>15s}    {:>6s}    {:>6s}    {:s}\n'.format(change, percent_change, point_change, label)

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

