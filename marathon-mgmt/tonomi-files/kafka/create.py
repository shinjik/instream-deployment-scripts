#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from kafka import *
from lambdas import *

args = parse_args()
marathon_client = get_marathon_client(args)

instances = {}

for instance_id, app in args['launch-instances'].items():
  configuration = app.get('configuration')
  env_name = configuration.get('configuration.name')
  tonomi_cluster_name = '/{}/kafka'.format(env_name)

  # try:
  zookeeper_node = marathon_client.get_app('/{}/zookeeper-3'.format(env_name))
  zookeeper_host = zookeeper_node.tasks[0].host
  zookeeper_port = zookeeper_node.env['ZOO_PORT']

  kafka_app = KafkaCluster(env_name, zookeeper_host, zookeeper_port, marathon_client)
  kafka_app.create()

  instances[tonomi_cluster_name] = {
    'instanceId': instance_id,
    'name': tonomi_cluster_name,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }
  # except:
  #   instance_results[tonomi_cluster_name] = {
  #     'instanceId': tonomi_cluster_id,
  #     'name': tonomi_cluster_name,
  #     '$set': {
  #       'status.flags.converging': True,
  #       'status.flags.active': False,
  #       'status.flags.failed': True
  #     }
  #   }

return_instances_info(instances)
