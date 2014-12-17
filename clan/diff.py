#!/usr/bin/env python

from collections import OrderedDict
import json
import os

from jinja2 import Environment, PackageLoader

from clan.utils import GLOBAL_ARGUMENTS, format_comma, format_duration, format_percent, load_field_definitions

class DiffCommand(object):
    def __init__(self):
        self.args = None
    
    def __call__(self, args):
        """
        Compare two data files and generate a report of their differences.
        """
        self.args = args
        self.field_definitions = load_field_definitions()

        with open(self.args.report_a_path) as f:
            report_a = json.load(f, object_pairs_hook=OrderedDict)

        with open(self.args.report_b_path) as f:
            report_b = json.load(f, object_pairs_hook=OrderedDict)

        diff = self.diff(report_a, report_b)

        output_format = os.path.splitext(self.args.output_path)[1]

        if output_format == '.html':
            with open(self.args.output_path, 'w') as f:
                self.html(diff, f)
        elif output_format == '.json':
            with open(self.args.output_path, 'w') as f:
                json.dump(diff, f, indent=4)
        else:
            raise Exception('Unsupported output format: %s. Must be .html or .json.' % output_format) 

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
           'report_a_path',
            action='store',
            help='Path to a JSON file containing the initial report data.'
        )

        parser.add_argument(
           'report_b_path',
            action='store',
            help='Path to a JSON file containing the report data to compare.'
        )

        parser.add_argument(
            'output_path',
            action='store',
            help='Path to output either an HTML report or a JSON data file.'
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
                        data_type = diff['data_types'][metric]
                        diff['data'][metric] = OrderedDict()

                        total_a = values['total']
                        total_b = query_b['data'][metric]['total']

                        for label, value in values.items():
                            a = value
                            
                            try:
                                b = query_b['data'][metric][label]
                            # TODO: hack for when labels are different...
                            except KeyError:
                                continue

                            change = b - a
                            percent_change = float(change) / a if a > 0 else None
                            
                            percent_a = float(a) / total_a if total_a > 0 else None
                            percent_b = float(b) / total_b if total_b > 0 else None

                            if label == 'total' or data_type == 'TIME' or percent_a is None or percent_b is None:
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
            point_change = '{:.1f}'.format(values['point_change'] * 100) if values['point_change'] is not None else '-'

            if values['change'] > 0:
                change = '+%s' % change

            if values['percent_change'] is not None and values['percent_change'] > 0:
                percent_change = '+%s' % percent_change

            if values['point_change'] is not None and values['point_change'] > 0:
                point_change = '+%s' % point_change

            return '{:>15s}    {:>8s}    {:>8s}    {:s}\n'.format(change, percent_change, point_change, label)

        context = {
            'diff': diff,
            'field_definitions': self.field_definitions,
            'GLOBAL_ARGUMENTS': GLOBAL_ARGUMENTS,
            'format_comma': format_comma,
            'format_duration': format_duration,
            'format_percent': format_percent,
            'format_row': format_row
        }

        f.write(template.render(**context).encode('utf-8'))

    def html(self, diff, f):
        """
        Generate a text report for a diff.
        """
        env = Environment(loader=PackageLoader('clan', 'templates'))

        template = env.get_template('diff.html')

        def number_class(v):
            if v is None:
                return ''

            if v > 0:
                return 'positive'
            elif v < 0:
                return 'negative'

            return ''

        context = {
            'diff': diff,
            'GLOBAL_ARGUMENTS': GLOBAL_ARGUMENTS,
            'format_comma': format_comma,
            'format_duration': format_duration,
            'number_class': number_class

        }

        f.write(template.render(**context).encode('utf-8'))

