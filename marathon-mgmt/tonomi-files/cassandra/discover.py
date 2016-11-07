#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from lambdas import *
from manager import *

args = parse_args()
manager = MarathonManager(get_marathon_url(args))
instances = {}

for instance_name in manager.discover(app_filter='cassandra'):
  instances[instance_name] = {
    'name': instance_name,
    'interfaces': {
      'info': {
        'signals': {
          'app-id': instance_name
        }
      }
    }
  }

return_instances_info(instances)
