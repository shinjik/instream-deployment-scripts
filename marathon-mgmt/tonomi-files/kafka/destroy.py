#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from lambdas import *

args = parse_args()
marathon_client = get_marathon_client(args)

instances = {}

for instance_name in args['instances'].keys():
  try:
    marathon_client.delete_app(instance_name)
  except:
    pass

  instances[instance_name] = {
    '$set': {
      'status.flags.converging': False,
      'status.flags.active': False
    }
  }

return_instances_info(instances)
