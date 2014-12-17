#!/usr/bin/env python

import os

from oauth2client import client
from oauth2client.file import Storage
from oauth2client import tools

class AuthCommand(object):
    def __init__(self):
        self.args = None

    def __call__(self, args):
        self.args = args 

        if not self.args.secrets:
            home_path = os.path.expanduser('~/.clan_secrets.json')

            if os.path.exists('client_secrets.json'):
                self.args.secrets = 'client_secrets.json'
            elif os.path.exists(home_path):
                self.args.secrets = home_path
            else:
                raise Exception('Could not locate authentication secrets (client_secrets.json). Please create it or specify a different file using --secrets.')

        storage = Storage('analytics.dat')
        
        flow = client.flow_from_clientsecrets(
            self.args.secrets,
            scope='https://www.googleapis.com/auth/analytics.readonly'
        )
        
        tools.run_flow(flow, storage, self.args)

    def add_argparser(self, root, parents):
        """
        Add arguments for this command.
        """
        parents.append(tools.argparser)

        parser = root.add_parser('auth', parents=parents)
        parser.set_defaults(func=self)

        parser.add_argument(
            '--secrets',
            dest='secrets', action='store',
            help='Path to the authorization secrets file (client_secrets.json).'
        )

        return parser

