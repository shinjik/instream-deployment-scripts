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
    app = marathon_client.get_app('{}/spark-app'.format(instance_name))

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
          'disk': app.disk * app.tasks_running,
          'instances': app.tasks_running
        }
      },
      'spark': {
        'signals': {
          'hosts': [],
          'load-balancer-port': '123'
        }
      }
    }

    components = {
      'spark-worker': {
        'reference': {
          'mapping': 'apps.app-by-id',
          'key': app.id
        }
      }
    }

    instances[instance_name] = {
      'instanceId': instance_name,
      'name': instance_name,
      'status': status,
      'interfaces': interfaces,
      'components': components,
    }
  except:
    instances[instance_name] = {
      'status': {
        'flags': {
          'active': False,
          'converging': False,
          'failed': False
        }
      }
    }

return_instances_info(instances)
