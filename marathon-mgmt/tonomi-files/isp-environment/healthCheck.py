#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from lambdas import *

args = parse_args()
marathon_client = get_marathon_client(args)

marathon_node_hostname = marathon_url.split(':')[1][2:]

instances = {}

for tonomi_env_name in args['instances'].keys():

  envs = []
  # for app in marathon_client.list_apps():
  #   for label, value in app.labels.items():
  #     if label == '_tonomi_environment':
  #       if value and value not in envs:
  #         envs.append(value)

  envs = [e.id.replace('/', '') for e in marathon_client.list_groups()]

  if tonomi_env_name in envs:

    status = {
      'flags': {
        'active': True,
        'converging': False,
        'failed': False
      }
    }

    env = marathon_client.get_group(tonomi_env_name)

    interfaces = {}
    components = {}  # multidict()

    for app in env.apps:
      env_name = env.id.replace('/', '')
      app_type = app.labels['_tonomi_application']

      app = marathon_client.get_app(app.id)

      if app_type == 'zookeeper':
        interfaces[app_type] = {
          'signals': {
            'zookeeper-hosts': [],
            'zookeeper-port': app.env['ZOO_PORT']
          }
        }
      elif app_type == 'redis':
        interfaces[app_type] = {
          'signals': {
            'master-hosts': [],
            'slave-hosts': [],
            'port': app.env['REDIS_PORT']
          }
        }
      elif app_type == 'cassandra':
        interfaces[app_type] = {
          'signals': {
            'seed-hosts': [],
            'node-hosts': [],
            'jmx-port': app.labels['_jmx_port'],
            'internode-communication-port': app.labels['_internode_communication_port'],
            'tls-internode-commucation-port': app.labels['_tls_internode_communication_port'],
            'thrift-client-port': app.labels['_thrift_client_port'],
            'cql-native-port': app.labels['_cql_native_port']
          }
        }
      elif app_type == 'kafka':
        interfaces[app_type] = {
          'signals': {
            'kafka-hosts': [task.host for task in app.tasks],
            'kafka-port': app.env['KAFKA_PORT']
          }
        }
      elif app_type == 'webui':
        service_port = str(app.container.docker.port_mappings[0].service_port)

        interfaces[app_type] = {
          'signals': {
            'load-balancer-port': service_port,
            'link': 'http://{}:{}'.format(marathon_node_hostname, service_port),
            'hosts': [task.host for task in app.tasks]
          }
        }

        interfaces['application-entrypoint'] = {
          'signals': {
            'URL': 'http://{}:{}'.format(marathon_node_hostname, service_port)
          }
        }

      elif app_type == 'spark':
        service_port = app.container.docker.port_mappings[2].service_port

        interfaces[app_type] = {
          'signals': {
            'hosts': [task.host for task in app.tasks],
            'web-interface': 'http://{}:{}'.format(marathon_node_hostname, service_port)
          }
        }

      components[app_type] = {
        'reference': {
          'mapping': '{}.{}-by-id'.format(app_type, app_type),
          'key': '/{}/{}'.format(env_name, app_type)
        }
      }

    instances[tonomi_env_name] = {
      'instanceId': tonomi_env_name,
      'name': tonomi_env_name,
      'status': status,
      'interfaces': interfaces,
      'components': components,
    }

  else:
    instances[tonomi_env_name] = {
      'status': {
        'flags': {
          'active': False,
          'converging': False,
          'failed': False
        }
      }
    }

return_instances_info(instances)
