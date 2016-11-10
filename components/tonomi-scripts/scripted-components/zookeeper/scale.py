#!/usr/bin/env python3

import sys
import json
import yaml
from marathon import MarathonClient
from utils import *

args = parse_args()
marathon_client = get_marathon_client(args)
instances = {}

for instance_name, app in args['instances'].items():
  command_id, command_info = next(iter(app['commands']).items())
  instances_num = command_info['control']['scale']['instances']

  try:
    marathon_client.scale_app('{}'.format(instance_name), instances_num, force=True)

    instances[instance_name] = {
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
    instances[instance_name] = {
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

return_instances_info(instances)
