#!/usr/bin/env python3

import sys
import json
import yaml
from marathon import MarathonClient


args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL', '')
marathon_client = MarathonClient(marathon_url)

instance_results = {}

for tonomi_instance_name in args.get('instances', {}).keys():
  command_id = list(args.get('instances', {}).get(tonomi_instance_name).get('commands').keys())[0]

  instances_number = args.get('instances', {}).get(tonomi_instance_name).get('commands').get(command_id) \
    .get('control').get('scale').get('instances')

  try:
    marathon_client.scale_app('{}-node'.format(tonomi_instance_name), instances_number, force=True)

    instance_results[tonomi_instance_name] = {
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
  except:
    instance_results[tonomi_instance_name] = {
      '$pushAll': {
        'commands.{}'.format(command_id): [
          {'$intermediate': True},
          {'status.flags.converging': True}
        ],
      },
      '$set': {
        'status.flags.converging': True,
        'status.flags.active': False,
        'status.flags.failed': True
      }
    }

yaml.safe_dump({ 'instances': instance_results }, sys.stdout)
