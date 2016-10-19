#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient


args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL', '')
marathon_client = MarathonClient(marathon_url)

instance_results = {}

for env_id in args.get('instances', {}).keys():
  for app in marathon_client.list_apps():
    if ('_tonomi_environment', env_id) in app.labels.items():
      try:
        marathon_client.delete_app(app_id, True)
      except:
        pass

  try:
    marathon_client.delete_group(env_id, True)
  except:
    pass

  instance_results[env_id] = {}

yaml.safe_dump({ 'instances': instance_results }, sys.stdout)
