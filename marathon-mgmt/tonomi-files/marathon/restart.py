#!/usr/bin/env python3

import sys
import json
import yaml
from marathon import MarathonClient


args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL', '')

marathon_client = MarathonClient(marathon_url)

instance_results = {}

for app_id in args.get('instances', {}).keys():
  command_id = list(args.get('instances', {}).get(app_id).get('commands').keys())[0]

  marathon_client.restart_app(app_id)

  instance_results[app_id] = {
    '$pushAll': {
      'commands.' + command_id: [{'$intermediate': True}, {'status.flags.converging': True}]
    },
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

yaml.safe_dump({ 'instances': instance_results }, sys.stdout)
