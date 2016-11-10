#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from utils import *
from models import *

args = parse_args()
manager = MarathonManager(get_marathon_url(args))
instances = {}

for instance_name in args['instances'].keys():
  manager.destroy(instance_name)

  instances[instance_name] = {
    '$set': {
      'status.flags.converging': False,
      'status.flags.active': False,
      'status.flags.failed': False
    }
  }

return_instances_info(instances)
