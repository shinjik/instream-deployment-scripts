#!/usr/bin/env python3

from marathon import MarathonClient
import sys
import json
import requests
import yaml

args = yaml.safe_load(sys.stdin)
marathon_url = args['configuration']['configuration.marathonURL']
marathon_client = MarathonClient(marathon_url)

instance_results = {}

for app in marathon_client.list_apps():
  instance_results[app.id] = {
    'name': app.id,
    'interfaces': {
      'info': {
        'signals': {
          'app-id': app.id
        }
      }
    }
  }

yaml.safe_dump({'instances': instance_results}, sys.stdout)
