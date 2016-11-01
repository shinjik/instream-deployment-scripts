#!/usr/bin/env python3

import sys
import json
import requests
import yaml
from marathon import MarathonClient

args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL')

marathon_client = MarathonClient(marathon_url)

result = {'instances': {}}

for app in marathon_client.list_apps():
  if '_tonomi_environment' in app.labels and '_tonomi_application' in app.labels:
    result['instances'][app.id] = {
      'name': app.id,
      'interfaces': {
        'info': {
          'signals': {
            'app-id': app.id
          }
        }
      }
    }

yaml.safe_dump(result, sys.stdout)
