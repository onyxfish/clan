#!/usr/bin/env python

from collections import OrderedDict
import json

from commands.utils import GLOBAL_ARGUMENTS

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

        output = OrderedDict([
            ('a', OrderedDict([(arg, report_a[arg]) for arg in GLOBAL_ARGUMENTS])),
            ('b', OrderedDict([(arg, report_b[arg]) for arg in GLOBAL_ARGUMENTS])),
            ('queries', [])
        ])

        for query_a in report_a['queries']:
            for query_b in report_b['queries']:
                if query_a['config'] == query_b['config']:
                    print 'Match: %s' % query_a['config']['name']

            query_b = report_b['queries']

        return output 

    def txt_diff(self, diff):
        """
        Generate a text report for a diff.
        """
        pass


