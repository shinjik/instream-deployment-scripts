#!/usr/bin/env python3

import sys
import yaml
from collections import defaultdict
from yaml.representer import SafeRepresenter
from marathon import MarathonClient

# to serialize defaultdicts normally
SafeRepresenter.add_representer(defaultdict, SafeRepresenter.represent_dict)


def multidict():
  return defaultdict(multidict)


args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL')
marathon_client = MarathonClient(marathon_url)

env_statuses = {}

for tonomi_env_name in args.get('instances', {}).keys():

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

    interfaces = {
      'application-entrypoint': {
        'signals': {
          'URL': 'https://host123.com' #ui.tasks[0].host
        }
      }
    }

    components = multidict()

    for app in env.apps:
      env_name = env.id.replace('/', '')
      app_type = app.labels['_tonomi_application']

      app = marathon_client.get_app(app.id)

      if app_type == 'zookeeper':
        interfaces[app_type] = {
          'signals': {
            'zookeeper-hosts': ['123', '123'],
            'zookeeper-port': app.env['ZOO_PORT']
          }
        }
      elif app_type == 'cassandra':
        interfaces[app_type] = {
          'signals': {
            'seed-hosts': '123',
            'node-hosts': '123',
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
        interfaces[app_type] = {
          'signals': {
            'link': '123',
            'load-balancer-port': '123',
            'hosts': '123'
          }
        }

      components[app_type] = {
        'reference': {
          'mapping': '{}.{}-by-id'.format(app_type, app_type),
          'key': '/{}/{}'.format(env_name, app_type)
        }
      }

    env_statuses[tonomi_env_name] = {
      'instanceId': tonomi_env_name,
      'name': tonomi_env_name,
      'status': status,
      'interfaces': interfaces,
      'components': components,
    }

  else:
    env_statuses[tonomi_env_name] = {
      'status': {
        'flags': {
          'active': False,
          'converging': False,
          'failed': False
        }
      }
    }

yaml.safe_dump({ 'instances': env_statuses }, sys.stdout)
