#!/usr/bin/env python3

import sys
import json
import yaml
from marathon import MarathonClient
from utils import *

args = parse_args()
marathon_client = get_marathon_client(args)

instances = {}

for instance_name in args['instances'].keys():
  try:
    marathon_client.delete_app(instance_name, True)

    instances[instance_name] = {
      '$set': {
        'status.flags.converging': False,
        'status.flags.active': False,
        'status.flags.failed': False
      }
    }
  except:
    instances[instance_name] = {
      '$set': {
        'status.flags.converging': False,
        'status.flags.active': False,
        'status.flags.failed': False
      }
    }

return_instances_info(instances)
