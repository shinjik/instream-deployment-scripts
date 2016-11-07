#!/usr/bin/env python3

import sys
import json
import yaml
from marathon import MarathonClient
from lambdas import *

args = parse_args()
marathon_client = get_marathon_client(args)
instances = {}

for app in marathon_client.list_apps():
  instances[app.id] = {
    'name': app.id,
    'interfaces': {
      'info': {
        'signals': {
          'app-id': app.id
        }
      }
    }
  }

return_instances_info(instances)
