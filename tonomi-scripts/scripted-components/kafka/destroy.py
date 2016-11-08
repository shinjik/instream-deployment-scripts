#!/usr/bin/env python3

import sys
import yaml
from lambdas import *
from models import *

args = parse_args()
manager = MarathonManager(get_marathon_url(args))
instances = {}

for instance_name in args['instances'].keys():
  manager.destroy(instance_name)

  instances[instance_name] = {
    '$set': {
      'status.flags.converging': False,
      'status.flags.active': False
    }
  }

return_instances_info(instances)
