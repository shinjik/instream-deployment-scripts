#!/usr/bin/env python3

import sys
import yaml
from collections import defaultdict
from yaml.representer import SafeRepresenter
from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonConstraint

# to serialize defaultdicts normally
SafeRepresenter.add_representer(defaultdict, SafeRepresenter.represent_dict)


def multidict():
  return defaultdict(multidict)


args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL')
marathon_client = MarathonClient(marathon_url)

app_statuses = {}

for tonomi_cluster_instance_name in args.get('instances', {}).keys():
  env_name = tonomi_cluster_instance_name.split('/')[1]

  cluster_exist = False
  list_apps = marathon_client.list_apps()
  for app in list_apps:
    if '/{}/zookeeper'.format(env_name) in app.id:
      cluster_exist = True

  if cluster_exist:
    nodes = []
    for app in marathon_client.list_apps():
      if '/{}/zookeeper'.format(env_name) in app.id:
        nodes.append(marathon_client.get_app(app.id))

    client_conn_port = nodes[0].labels['_client_conn_port']
    follower_conn_port = nodes[0].labels['_follower_conn_port']
    server_conn_port = nodes[0].labels['_server_conn_port']

    # reconfigure cluster nodes
    # active_apps = []
    # for node in nodes:
    #   if node.tasks_running > 0:
    #     active_apps.append((node.id, node.id.split('-')[1], node.tasks[0].host))
    #
    # zoo_servers = ''
    #
    # for node_id, index, host in active_apps:
    #   zoo_servers += 'server.{}={}:{}:{} '.format(index, host, follower_conn_port, server_conn_port)
    #
    # new_cmd = 'export ZOO_SERVERS="{}" && /docker-entrypoint.sh zkServer.sh start-foreground'.format(zoo_servers)
    #
    # for node_id, index, host in active_apps:
    #   constraints = [MarathonConstraint(field='hostname', operator='LIKE', value=host)]
    #   app = marathon_client.get_app(node_id)
    #   if app.cmd != new_cmd:
    #     app.cmd = new_cmd
    #     app.constraints = constraints
    #     marathon_client.update_app(node_id, app, True)

    node_app = marathon_client.get_app('/{}/zookeeper-1'.format(env_name))

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
          'ram':  node_app.mem * node_tasks_running,
          'cpu':  node_app.cpus * node_tasks_running,
          'disk': node_app.disk * node_tasks_running
        }
      },
      'zookeeper': {
        'signals': {
          'zookeeper-hosts': list(set(zookeeper_hosts)),
          'zookeeper-ports': [client_conn_port, follower_conn_port, server_conn_port]
        }
      }
    }

    components = multidict()
    components['zookeeper-node'] = {
      'reference': {
        'mapping': 'apps.app-by-id',
        'key': '/{}/zookeeper'.format(env_name)
      }
    }

    app_statuses[tonomi_cluster_instance_name] = {
      'instanceId': tonomi_cluster_instance_name,
      'name': tonomi_cluster_instance_name,
      'status': status,
      'interfaces': interfaces,
      'components': components,
    }

  else:
    app_statuses[tonomi_cluster_instance_name] = {
      'status': {
        'flags': {
          'active': False,
          'converging': False,
          'failed': False
        }
      }
    }

yaml.safe_dump({ 'instances': app_statuses }, sys.stdout)
