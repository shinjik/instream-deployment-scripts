#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from utils import *

args = parse_args()
marathon_client = get_marathon_client(args)
instances = {}

for instance_name in args['instances'].keys():

  # try:
    group = marathon_client.get_group(instance_name)
    app = marathon_client.get_app(group.apps[0].id)

    status = {
      'flags': {
        'active': True,
        'converging': False,
        'failed': app.tasks_unhealthy > 0
      }
    }

    interfaces = {
      'compute': {
        'signals': {
          'ram': app.mem * app.tasks_running,
          'cpu': app.cpus * app.tasks_running,
        }
      }
    }

    instances[instance_name] = {
      'instanceId': instance_name,
      'name': instance_name,
      'status': status,
      'interfaces': interfaces,
      'components': {},
    }
  # except:
  #   instances[instance_name] = {
  #     'status': {
  #       'flags': {
  #         'active': False,
  #         'converging': False,
  #         'failed': False
  #       }
  #     }
  #   }

return_instances_info(instances)
