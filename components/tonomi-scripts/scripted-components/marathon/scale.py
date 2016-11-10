#!/usr/bin/env python3

import sys
import json
import yaml
from marathon import MarathonClient
from utils import *

args = parse_args()
marathon_client = get_marathon_client(args)

instances = {}

for instance_name, instance in args['instances'].items():
  command_id, command_info = next(iter(instance['commands'].items()))
  instances_num = command_info['control']['scale']['instances']
  marathon_client.scale_app(instance_name, instances_num, force=True)

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

return_instances_info(instances)
