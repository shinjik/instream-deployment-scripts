#!/usr/bin/env python3

import sys
import yaml
from lambdas import *

args = parse_args()
marathon_client = get_marathon_client(args)
instances = {}

for instance_name in args['instances'].keys():

  try:
    nodes = []
    for app in marathon_client.list_apps():
      if '{}/zookeeper'.format(instance_name) in app.id:
        nodes.append(marathon_client.get_app(app.id))

    client_conn_port = nodes[0].labels['_client_conn_port']
    follower_conn_port = nodes[0].labels['_follower_conn_port']
    server_conn_port = nodes[0].labels['_server_conn_port']

    node_app = nodes[0]

    status = {
      'flags': {
        'active': True,
        'converging': False,
        'failed': node_app.tasks_unhealthy > 0
      }
    }

    node_tasks_running = node_app.tasks_running

    zookeeper_hosts = []
    for node in nodes:
      for task in node.tasks:
        zookeeper_hosts.append(task.host)

    interfaces = {
      'compute': {
        'signals': {
          'ram': node_app.mem * node_tasks_running,
          'cpu': node_app.cpus * node_tasks_running,
          'disk': node_app.disk * node_tasks_running
        }
      },
      'zookeeper': {
        'signals': {
          'zookeeper-hosts': zookeeper_hosts,
          'zookeeper-ports': [client_conn_port, follower_conn_port, server_conn_port]
        }
      }
    }

    components = {}

    for node in nodes:
      components['zookeeper-{}'.format(node.id.split('-')[-1])] = {
        'reference': {
          'mapping': 'apps.app-by-id',
          'key': '{}'.format(node.id)
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
