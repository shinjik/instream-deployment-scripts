#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from lambdas import *

args = parse_args()
marathon_client = get_marathon_client(args)
instances = {}

for app in marathon_client.list_apps():
  if ('_tonomi_application', 'spark') in app.labels.items():
    env_name = app.labels['_tonomi_environment']
    instance_name = '/{}/spark'.format(env_name)
    instances[instance_name] = {
      'name': instance_name,
      'interfaces': {
        'info': {
          'signals': {
            'app-id': instance_name
          }
        }
      }
    }

return_instances_info(instances)
