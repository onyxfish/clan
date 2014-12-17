#!/usr/bin/env python

import json
import os

import requests

GLOBAL_ARGUMENTS = [
    'property-id',
    'start-date',
    'end-date',
    'ndays',
    'domain',
    'prefix',
] 

FIELD_DEFINITIONS_URL = 'https://www.googleapis.com/analytics/v3/metadata/ga/columns'
FIELD_DEFINITIONS_PATH = os.path.expanduser('~/.clan_defs.json')

def load_field_definitions():
    if os.path.exists(FIELD_DEFINITIONS_PATH):
        with open(FIELD_DEFINITIONS_PATH) as f:
            fields = json.load(f)
    else:
        response = requests.get(FIELD_DEFINITIONS_URL)

        if not response.status_code == 200:
            raise Exception('Failed to fetch field definitions from Google!')

        data = response.json()

        fields = {}

        for item in data['items']:
            fields[item['id']] = {
                'type': item['attributes']['type'],
                'dataType': item['attributes']['dataType'],
                'uiName': item['attributes']['uiName'],
                'description': item['attributes']['description']
            }

        with open(FIELD_DEFINITIONS_PATH, 'w') as f:
            json.dump(fields, f)

    return fields

def format_comma(d):
    """
    Format a comma separated number.
    """
    return '{:,d}'.format(int(d))

def format_duration(secs):
    """
    Format a duration in seconds as minutes and seconds.
    """
    secs = int(secs)

    if abs(secs) > 60:
        mins = abs(secs) / 60
        secs = abs(secs) - (mins * 60)

        return '%s%im %02is' % ('-' if secs < 0 else '', mins, secs)

    return '%is' % secs

def format_percent(d, t):
    """
    Format a value as a percent of a total.
    """
    return '{:.1%}'.format(float(d) / t)

