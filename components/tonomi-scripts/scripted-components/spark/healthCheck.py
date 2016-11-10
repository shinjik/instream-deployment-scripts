#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from utils import *

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
          'hosts': [task.host for task in app.tasks],
          'load-balancer-port': app.container.docker.port_mappings[2].service_port
        }
      }
    }

    components = {
      'spark': {
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
