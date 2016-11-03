#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from lambdas import *

args = parse_args()
marathon_client = get_marathon_client(args)
instances = {}

for env_id in args['instances'].keys():
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

  instances[env_id] = {}

return_instances_info(instances)
