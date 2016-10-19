#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient

args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL')

marathon_client = MarathonClient(marathon_url)

result = {'instances': {}}

envs = []

for group in marathon_client.list_groups():
  if len(group.apps) == 0:
    marathon_client.delete_group(group.id)

for app in marathon_client.list_apps():
  for label, value in app.labels.items():
    if label == '_tonomi_environment':
      if value and value not in envs:
        envs.append(value)

for env_name in envs:
  result['instances'][env_name] = {
    'name': env_name,
    'interfaces': {
      'info': {
        'signals': {
          'app-id': env_name
        }
      }
    }
  }

yaml.safe_dump(result, sys.stdout)
