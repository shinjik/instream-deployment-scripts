#!/usr/bin/env python3

from marathon import MarathonClient
import sys
import json
import yaml

args = yaml.safe_load(sys.stdin)
marathon_url = args['configuration']['configuration.marathonURL']
marathon_client = MarathonClient(marathon_url)

instance_results = {}

for instance_name in args['instances'].keys():
  try:
    marathon_client.delete_app(instance_name, True)

    instance_results[instance_name] = {
      '$set': {
        'status.flags.converging': False,
        'status.flags.active': False,
        'status.flags.failed': False
      }
    }
  except:
    instance_results[instance_name] = {
      '$set': {
        'status.flags.converging': False,
        'status.flags.active': False,
        'status.flags.failed': False
      }
    }

yaml.safe_dump({'instances': instance_results}, sys.stdout)
