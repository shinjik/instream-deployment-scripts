#!/usr/bin/env python3

from marathon import MarathonClient
import sys
import json
import yaml

args = yaml.safe_load(sys.stdin)
marathon_url = args['configuration']['configuration.marathonURL']
marathon_client = MarathonClient(marathon_url)

instance_results = {}

for instance_name, instance in args['instances'].items():
  command_id = next(iter(instance['commands'].items()))[0]
  marathon_client.restart_app(instance_name)

  instance_results[instance_name] = {
    '$pushAll': {
      'commands.{}'.format(command_id): [
        {'$intermediate': True},
        {'status.flags.converging': True}
      ]
    },
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

yaml.safe_dump({'instances': instance_results}, sys.stdout)
