#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from utils import *
from models import *

args = parse_args()
manager = MarathonManager(get_marathon_url(args))
marathon_client = MarathonClient(get_marathon_url(args))
instances = {}

for instance_name in sorted(args['instances'].keys()):
  try:
    seed_app = marathon_client.get_app('{}/cassandra-seed'.format(instance_name))
    node_app = marathon_client.get_app('{}/cassandra-node'.format(instance_name))

    status = {
      'flags': {
        'active': True,
        'converging': False,
        'failed': seed_app.tasks_unhealthy > 0
      }
    }

    seed_tasks_running = seed_app.tasks_running
    node_tasks_running = node_app.tasks_running

    interfaces = {
      'compute': {
        'signals': {
          'ram': seed_app.mem * seed_tasks_running + node_app.mem * node_tasks_running,
          'cpu': seed_app.cpus * seed_tasks_running + node_app.cpus * node_tasks_running,
          'disk': seed_app.disk * seed_tasks_running + node_app.disk * node_tasks_running
        }
      },
      'cassandra': {
        'signals': {
          'seed-hosts': [seed_task.host for seed_task in seed_app.tasks],
          'node-hosts': [node_task.host for node_task in node_app.tasks],
          'jmx-port': seed_app.labels['_jmx_port'],
          'internode-communication-port': seed_app.labels['_internode_communication_port'],
          'tls-internode-communication-port': seed_app.labels['_tls_internode_communication_port'],
          'thrift-client-port': seed_app.labels['_thrift_client_port'],
          'cql-native-port': seed_app.labels['_cql_native_port']
        }
      }
    }

    components = {
      'cassandra-seed': {
        'reference': {
          'mapping': 'apps.app-by-id',
          'key': '{}/cassandra-seed'.format(instance_name)
        }
      },
      'cassandra-node': {
        'reference': {
          'mapping': 'apps.app-by-id',
          'key': '{}/cassandra-node'.format(instance_name)
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
