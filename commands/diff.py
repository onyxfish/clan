#!/usr/bin/env python

from collections import OrderedDict
import json

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
                self.txt_diff(diff, f)
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
            dest='format', action='store', default='txt', choices=['txt', 'json'],
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

    def txt_diff(self, diff, f):
        """
        Generate a text report for a diff.
        """
        f.write('Comparing report A run %s with:\n' % diff['a']['run_date'])
    
        for var in GLOBAL_ARGUMENTS:
            if diff['a'].get(var, None):
                f.write('    %s: %s\n' % (var , diff['a'][var]))

        f.write('\n')

        f.write('With report B run %s with:\n' % diff['b']['run_date'])

        for var in GLOBAL_ARGUMENTS:
            if diff['b'].get(var, None):
                f.write('    %s: %s\n' % (var , diff['b'][var]))

        TODO="""
        for analytic in diff['queries']:
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
                        pct = format_percent(value, total) if total > 0 else '0.0%' 
                        value = format_comma(value)
                    elif data_type == 'TIME':
                        pct = '-'
                        value = format_duration(value)
                    elif data_type in ['FLOAT', 'CURRENCY', 'PERCENT']:
                        pct = '-'
                        value = '%.1f' % value

                    f.write('{:>15s}    {:>6s}    {:s}\n'.format(value, pct, label))

                f.write('\n')

            f.write('\n')"""
