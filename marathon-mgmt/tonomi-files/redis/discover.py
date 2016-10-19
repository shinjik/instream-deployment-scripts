#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient


args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL')
marathon_client = MarathonClient(marathon_url)

result = {'instances': {}}

for app in marathon_client.list_apps():
  if ('_tonomi_application', 'redis') in app.labels.items():
    env_name = app.labels['_tonomi_environment']
    tonomi_cluster_name = '/{}/redis'.format(env_name)
    result['instances'][tonomi_cluster_name] = {
      'name': tonomi_cluster_name,
      'interfaces': {
        'info': {
          'signals': {
            'app-id': tonomi_cluster_name
          }
        }
      }
    }

yaml.safe_dump(result, sys.stdout)
