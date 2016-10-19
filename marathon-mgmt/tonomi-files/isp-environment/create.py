#!/usr/bin/env python3

import sys
import yaml
from marathon import MarathonClient
from marathon.models import MarathonApp, MarathonConstraint
from marathon.models.container import *
from marathon.models.app import PortDefinition, Residency
from cassandra import *
from zookeeper import *
from kafka import *
from redis import *
from webui import *
from spark import *
import time


args = yaml.safe_load(sys.stdin)
marathon_url = args.get('configuration', {}).get('configuration.marathonURL', '')

marathon_client = MarathonClient(marathon_url)

instance_results = {}

for env_id, env in args.get('launch-instances', {}).items():
  configuration = env.get('configuration')
  env_name = env.get('configuration').get('configuration.name')

  # 1. zookeeper cluster
  zookeeper_cluster = ZookeeperCluster(env_name, marathon_client)
  zookeeper_cluster.create()

  # 2. redis cluster
  redis_cluster = RedisCluster(env_name, marathon_client)
  redis_cluster.create()

  # 3. cassandra cluster
  cassandra_cluster = CassandraCluster(env_name, marathon_client)
  cassandra_cluster.create()

  # 4. kafka cluster
  zookeeper_node = marathon_client.get_app('/{}/zookeeper-1'.format(env_name))
  zookeeper_host = zookeeper_node.tasks[0].host
  zookeeper_port = zookeeper_node.env['ZOO_PORT']
  kafka_app = KafkaCluster(env_name, zookeeper_host, zookeeper_port, marathon_client)
  kafka_app.create()

  # TODO: populate apps!
  # 5. redis <- dictionaries,
  #    cassandra <- schema + movies list!

  # 6. web ui
  webui_app = WebUINodes(env_name, marathon_client)
  webui_app.create()

  # 7. spark app
  spark_app = SparkCluster(env_name, marathon_client)
  spark_app.create()

  instance_results[env_name] = {
    'instanceId': env_id,
    'name': env_name,
    '$set': {
      'status.flags.converging': True,
      'status.flags.active': False
    }
  }

yaml.safe_dump({'instances': instance_results}, sys.stdout)
